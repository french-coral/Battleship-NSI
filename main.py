import serial.tools.list_ports
import time
import random

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


#---------------------------------DEBUG---------------------------------#
#
#  Le temps de debug toute les fonctionalité concernant le plateau_2 seront desactivés,
#  à comment in si besoin.
#
#-----------------------------------------------------------------------#

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


def detect_devices():
    """
    Détecte les ports disponibles et assigne les ports aux plateaux en fonction de leur UID.
    Pour le moment, le code est configuré pour fonctionner avec un seul plateau (plateau_1).


    Testing purposes : Affiche l'etat des ports dispos
    La FeatherM4 devrait ressembler à ca:
    ----------
    Nom du port     : COM5 (ou COMx sous windows)
    Description     : Périphérique série USB (COM5)
    Fabricant       : Microsoft
    Produit         : None
    Numéro de série : 4657A1084E384B53202020522D4316FF (c'est celle du plateau_1)
    ----------
    """
    """
    # UID des plateaux
    uid_plateau_1 = "4657A1084E384B53202020522D4316FF"  # UID du plateau 1
    #uid_plateau_2 = "ICIMETTRELUIDDUPLATEAU2"  # UID du plateau 2 (à remplacer par le vrai UID)

    # Initialisation des ports
    port_plateau_1 = None
    #port_plateau_2 = None
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

        # Teste si le port est ouvert et peut communiquer eviter la diff entre console et usb_cdc.data
        print(f"Test du port : {port.device}")
        try:
            with serial.Serial(port.device, 9600, timeout=1) as port_serial:
                time.sleep(0.5)
                if port_serial.in_waiting:
                    response = lire(port_serial)
                    print(f"Réponse reçue sur {port.device} : {response}")

                    """
                    # Vérifie l'UID pour assigner les ports
                    if port.serial_number == uid_plateau_1:
                        print(f"Plateau 1 détecté sur le port {port.device}")
                        port_plateau_1 = safe_open(port.device)

                    #elif port.serial_number == uid_plateau_2:
                    #    print(f"Plateau 2 détecté sur le port {port.device}")
                    #    port_plateau_2 = safe_open(port.device)

                    """

                    return port.device
                
        except Exception as exept:
            print(f"Erreur avec le port {port.device} : {exept}")
            print("Le port est peut-être déjà utilisé. (console)\n")
    
    

    return None




# Test automatique des ports
port_detected = detect_devices()

if port_detected:
    print(f"Port fonctionnel détecté : {port_detected}")
else:
    print("Aucun port fonctionnel détecté.")


# Test automatique des ports
port_detected_1 = get_port_by_serial("4657A1084E384B53202020522D4316FF")  # UID du plateau 1
#port_detected_2 = get_port_by_serial("ICIMETTRELUIDDUPLATEAU2")  # UID du plateau 2 (à remplacer par le vrai UID)

port_plateau_1 = safe_open(port_detected_1) if port_detected_1 else None
#port_plateau_2 = safe_open(port_detected_2) if port_detected_2 else None

if port_plateau_1:
    print("Plateau 1 connecté.")
else:
    print("Plateau 1 non détecté.")

#if port_plateau_2:
    #print("Plateau 2 connecté.")
#else:
    #print("Plateau 2 non détecté.")
    
time.sleep(2)





p1_duo_activated = False
#p2_duo_activated = False


def game_ready(port_plateau_1):#, port_plateau_2):
    """
    Attend que les 2 plateaux soit dans le mode duo.
    """

    while not p1_duo_activated: # and not p2_duo_activated:

        time.sleep(0.1)

        if port_plateau_1:
            response_p1 = lire(port_plateau_1)
            if response_p1 == "DUOREADY":
                p1_duo_activated = True

        #if port_plateau_2:
        #    response_p2 = lire(port_plateau_2)
        #    if response_p2 == "DUOREADY":
        #        p2_duo_activated = True

    print("Mode duo activé pour les deux plateaux.\n")
    print("Demande de placement des plateaux.")
    start_game(port_plateau_1)#, port_plateau_2)


def start_game(port_plateau_1):#, port_plateau_2):
    """
    Fonction principale pour démarrer le jeu.
    Placement des bateaux, attente de la préparation des joueurs,
    """

    global game_running

    # Phase de placement des bateaux
    envoyer(port_plateau_1, "PLACE")
    #envoyer(port_plateau_2, "PLACE")
    ready1 = False
    while not ready1:# and not ready 2:
        cmd1 = lire(port_plateau_1)
        if cmd1 == "READY":
            ready1 = True
    print("Le joueur est prêt. Début de la partie.")
    game_running = True

    game_loop(port_plateau_1)#, port_plateau_2)


def game_loop(port_plateau_1):#, port_plateau_2):
    """
    Boucle principale du jeu.
    Gère les tours des joueurs, les tirs et les résultats.
    """
    
    global game_running
    
    while game_running:

        print("\n---- TOUR du Joueur 1 ----")
        envoyer(port_plateau_1, "YOURTURN")

        cmd = lire(port_plateau_1)
        if cmd and cmd.startswith("TIR:"):

            # Simule une réponse du second plateau
            _, coord = cmd.split(":")
            x, y = map(int, coord.split(","))
            print(f"Tir reçu en ({x}, {y})")

            # Simule un résultat aléatoire pour le debug
            result = random.choice(["RESULT:RATE", "RESULT:TOUCHE", "RESULT:COULE"])
            print(f"Résultat simulé : {result}")
            envoyer(port_plateau_1, result)

            if result == "RESULT:COULE":
                print("Un bateau a été coulé.")
            elif result == "RESULT:WIN":
                print("Le joueur 1 a gagné !")
                break


# Boucle principale du 1v1 p1 et p2 à remplacer part port_plateau_1 et port_plateau_2
"""
def game_loop(port_plateau_1):#, port_plateau_2):
    global game_running
    
    while game_running:

    # Phase de placement des bateaux
    envoyer(port_plateau_1, "PLACE")
    envoyer(port_plateau_2, "PLACE")

    ready1, ready2 = False, False
    while not (ready1 and ready2):
        if not ready1:
            cmd1 = lire(port_plateau_1)
            if cmd1 == "READY":
                ready1 = True
        if not ready2:
            cmd2 = lire(port_plateau_2)
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
            envoyer(port_plateau_1, "YOURTURN")
            cmd = lire(port_plateau_1)
            if cmd and cmd.startswith("TIR:"): # Detection de l'arrivée du tir
                envoyer(port_plateau_2, cmd)  # Envoie le tir au plateau 2
                result = lire(port_plateau_2)
                if result:
                    envoyer(port_plateau_1, result)  # Envoie le résultat au plateau 1
                    if result == "RESULT:WIN":
                        print("Le joueur 1 a gagné !")
                        break
            joueur_actuel = 1
        else:
            envoyer(port_plateau_2, "YOURTURN")
            cmd = lire(port_plateau_2)
            if cmd and cmd.startswith("TIR:"):
                envoyer(port_plateau_1, cmd)  # Envoie le tir au plateau 1
                result = lire(port_plateau_1)
                if result:
                    envoyer(port_plateau_2, result)  # Envoie le résultat au plateau 2
                    if result == "RESULT:WIN":
                        print("Le joueur 2 a gagné !")
                        break
            joueur_actuel = 0

        print("Partie terminée.")
        break"""