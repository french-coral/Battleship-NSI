import serial.tools.list_ports
import time

def detect_devices():
    """
    Testing purposes
    La FeatherM4 devrait ressembler à ca:
    ----------
    Nom du port     : COM5 (ou COMx sous windows)
    Description     : Périphérique série USB (COM5)
    Fabricant       : Microsoft
    Produit         : None
    Numéro de série : 4657A1084E384B53202020522D4316FF (c'est celle du plateau_1)
    ----------
    """
    ports = serial.tools.list_ports.comports()
    for port in ports:
        print("----------")
        print(f"Nom du port     : {port.device}")
        print(f"Description     : {port.description}")
        print(f"Fabricant       : {port.manufacturer}")
        print(f"Produit         : {port.product}")
        print(f"Numéro de série / UID : {port.serial_number}")
        print("----------")

detect_devices()


def get_port_by_serial(target_serial):
    """
    Récupère les ports qui recoive une UID précise,
    Ici:
    Plateau 1: 4657A1084E384B53202020522D4316FF
    Plateau 2: Unknown
    """
    ports = serial.tools.list_ports.comports()
    for port in ports:
        if port.serial_number == target_serial:
            return port.device
    return None

def safe_open(port_name, baud=9600, timeout=1):
    """
    Check si le port COMx est pas déjà utilisé autre part (au hassard l'IDE Mu)
    Si c'est bon alors il ouvre le port comme il faut
    """
    try:
        return serial.Serial(port_name, baud, timeout=timeout)
    except serial.SerialException as e:
        print(f"Erreur d'ouverture du port {port_name}: {e}")
        return None


#---------------------------------DEBUG---------------------------------#
#
#  Le temps de debug toute les fonctionalité concernant le plateau_2 seront desactivés,
#  à comment in si besoin.
#
#-----------------------------------------------------------------------#

port_plateau_1 = safe_open(get_port_by_serial("4657A1084E384B53202020522D4316FF")) # UID du plateau 1, voir boot_out.txt dans CIRCUITPY(D:)
#port_plateau_2 = safe_open(get_port_by_serial("ICIMETTRELUIDDUPLATEAU2"))

if port_plateau_1:
    p1 = port_plateau_1
    print("Plateau 1 connecté.")
#if port_plateau_2:
#    p2 = port_plateau_2
    print("Plateau 2 connecté.")
else:
    print("Aucun plateau connecté.")
time.sleep(2)

###########################################################################

    # La communication entre les plateaux et l'ordi/raspberri pi se fera a l'aide d'un protocole
    # de communication basé sur des messages simples.
    #
    # Exemple:
    #   Depuis le plateau (vers le script maître)
    #       PLACEMENT:x,y → un bouton a été appuyé
    #       TIR:x,y → le joueur a tiré ici
    #       FIN → le joueur a fini
    #
    #   Depuis le maître (vers le plateau):
    #       LED:x,y,color → allumer une LED (color = green/red/blue)
    #       RESET → reset le plateau
    #       VICTOIRE → allumer toutes les LED en vert (par exemple)
    #       GAMEOVER → game over, les LED s'éteignent
    #       SCORE:x,y,valeur → afficher le score
    #
    #
    # Les fonctions suivante sont là pour decrypter les messages et les envoyés.
    # lire(plateau): plateau étant le serial du plateau
    # envoyer(plateau,message): plateau étant le serial du plateau et message le message à envoyer
    
###########################################################################

def envoyer(plateau, message):
    try:
        print(f'<<< {message}')  # Débogage
        plateau.write((message + "\n").encode())
    except Exception as exept:
        print(f'Erreur envoi : {exept}')

def lire(plateau): 
    if plateau.in_waiting:
        try:
            msg = plateau.readline().decode().strip()
            print(f'>>> {msg}')  # Débogage
            return msg
        except Exception as exept:
            print(f'Erreur de lecture : {exept}')
    return None





# Test de communication avec le plateau 1 seulement
envoyer(p1, "TEST")
time.sleep(0.5)
response = lire(p1)
if response:
    print(f"Réponse du plateau : {response}")
else:
    print("Aucune réponse du plateau.")

while not p1_duo_activated: # and not p2_duo_activated:

    time.sleep(0.1)
    envoyer(p1, "DUO?")
    #envoyer(p2, "DUO?") # Plateau 2
    response_p1 = lire(p1)
    #response_p2 = lire(p2) # Plateau 2
    if response_p1 is "YESDUO":
        p1_duo_activated = True
    #if response_p2 is "YESDUO":
        #p2_duo_activated = True


while True:
    # Phase de placement des bateaux
    envoyer(p1, "PLACE")
    ready1 = False
    while not ready1:
        cmd1 = lire(p1)
        if cmd1 == "READY":
            ready1 = True
    print("Le joueur est prêt. Début de la partie.")

    while True:
        print("\n---- TOUR du Joueur 1 ----")
        envoyer(p1, "YOURTURN")
        cmd = lire(p1)
        if cmd and cmd.startswith("TIR:"):
            # Simule une réponse du second plateau
            _, coord = cmd.split(":")
            x, y = map(int, coord.split(","))
            print(f"Tir reçu en ({x}, {y})")

            # Simule un résultat aléatoire
            import random
            result = random.choice(["RESULT:RATE", "RESULT:TOUCHE", "RESULT:COULE"])
            print(f"Résultat simulé : {result}")
            envoyer(p1, result)

            if result == "RESULT:COULE":
                print("Un bateau a été coulé.")
            elif result == "RESULT:WIN":
                print("Le joueur 1 a gagné !")
                break


# Boucle principale du 1v1
"""
while True:
    # Phase de placement des bateaux
    envoyer(p1, "PLACE")
    envoyer(p2, "PLACE")

    ready1, ready2 = False, False
    while not (ready1 and ready2):
        if not ready1:
            cmd1 = lire(p1)
            if cmd1 == "READY":
                ready1 = True
        if not ready2:
            cmd2 = lire(p2)
            if cmd2 == "READY":
                ready2 = True
    print("Les deux joueurs sont prêts. Début de la partie.")

    nom = ['Joueur 1','Joueur 2']
    joueur_actuel = 0

    while True:
        
       # Boucle principale du jeu.
       # Pour le moment test solo.


        
        print(f"\n---- TOUR du {nom[joueur_actuel]} ----") # Styling

        if joueur_actuel == 0:
            envoyer(p1, "YOURTURN")
            cmd = lire(p1)
            if cmd and cmd.startswith("TIR:"): # Detection de l'arrivée du tir
                envoyer(p2, cmd)  # Envoie le tir au plateau 2
                result = lire(p2)
                if result:
                    envoyer(p1, result)  # Envoie le résultat au plateau 1
                    if result == "RESULT:WIN":
                        print("Le joueur 1 a gagné !")
                        break
            joueur_actuel = 1
        else:
            envoyer(p2, "YOURTURN")
            cmd = lire(p2)
            if cmd and cmd.startswith("TIR:"):
                envoyer(p1, cmd)  # Envoie le tir au plateau 1
                result = lire(p1)
                if result:
                    envoyer(p2, result)  # Envoie le résultat au plateau 2
                    if result == "RESULT:WIN":
                        print("Le joueur 2 a gagné !")
                        break
            joueur_actuel = 0

        print("Partie terminée.")
        break"""