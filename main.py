import serial.tools.list_ports
import time
import random

connected_ports = {} # UID : serial.Serial object


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
        plateau.flush()
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

def get_port_by_serial(target_serial, detected_ports = None):
    """
    Récupère les ports qui recoive une UID précise,
    Ici:
    Plateau 1: 4657A1084E384B53202020522D4316FF
    Plateau 2: Unknown
    """
    if not detected_ports:
        detected_ports = serial.tools.list_ports.comports() # Debug temporaire 23/04

    for port in detected_ports:
        if port.serial_number == target_serial:
            return port.device
    return None

# Handshake PING/OK
def try_handshake(port_name, baud=9600, timeout=1.5):
    """
    Force la communication feather - server pour éviter d'avoir un timing pourri
    """
    try:
        with serial.Serial(port_name, baud, timeout=timeout) as ser:
            time.sleep(0.6) # laisse la Feather respirer

            ser.reset_input_buffer() # Soit disant plus clean mais ca pete tout
            ser.reset_output_buffer()

            print("Pinging ...\n")
            ser.write(b"PING\n")  # Commande bidon qui attend une réponse connue (ok)
            ser.flush()
            time.sleep(1)

            # On laisse un peu de marge pour la réponse
            if ser.in_waiting:
                response = ser.readline().decode().strip()
                print(f"Réponse sur {port_name} : {response}                                                                //!//      {response}")
                if response == "OK":
                    ser.write(b"RECEIVED\n")
                    return True
    except Exception as e:
        print(f"[!] Erreur de handshake sur {port_name} : {e}\n")
    return False

def safe_open(port_name, baud=9600, timeout=1):
    """
    Check si le port COMx est pas déjà utilisé autre part (au hassard l'IDE Mu)
    Si c'est bon alors il ouvre le port comme il faut
    """
    try:
        return serial.Serial(port_name, baud, timeout=timeout)
    except serial.SerialException as e:
        print(f"[!] Port occupé ou erreur sur {port_name} : {e}")
        return None

def check_connections():
    """
    Check de manière dynamique si un port est déconnecté, ca évite de relancer le script a chaque fois.
    """
    disconnected = []

    for port_name, ser in connected_ports.items():
        try:
            # Essaye de lire 1 byte, sans bloquer (timeout déjà défini)
            test = ser.read(1)
            if test == b'':  # Ça peut aussi être signe de port fermé (EOF)
                pass  # Pas une erreur
        except (serial.SerialException, OSError) as e:
            print(f"\n[X] Plateau déconnecté ({port_name}) : {e}")
            disconnected.append(port_name)

    for port_name in disconnected: # Retire le port proprement de là où il était (si on le rebranche y'a pas de problème)
        ser = connected_ports[port_name]
        try:
            ser.close()
        except:
            pass
        del connected_ports[port_name]
        print(f"[~] Port {port_name} nettoyé et retiré.\n")

def detect_devices(baud=9600, timeout=1):
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
   
    # UID des plateaux
    uid_plateau_1 = "4657A1084E384B53202020522D4316FF"  # UID du plateau 1
    #uid_plateau_2 = "ICIMETTRELUIDDUPLATEAU2"  # UID du plateau 2 (à remplacer par le vrai UID)

    # Initialisation des ports
    port_plateau_1 = None
    #port_plateau_2 = None
    """

    ports = serial.tools.list_ports.comports()
    new_feathers = []
    
    for port in ports:
         # Skip les ports Bluetooth connus (ils ouvrent mais n'envoie rien c'est chiant)
        if "Bluetooth" in port.description or "Bluetooth" in port.device:
            print(f"[IGNORÉ] Port Bluetooth détecté : {port.device}\n")
            continue
        
        #Skip les ports déjà connectés (c plus bo pour la console)
        if port.device in connected_ports:
            print(f"[IGNORÉ] Port déjà connecté : {port.device}\n")
            continue
            
        print("----------")
        print(f"Nom du port     : {port.device}")
        print(f"Description     : {port.description}")
        print(f"Fabricant       : {port.manufacturer}")
        print(f"Produit         : {port.product}")
        print(f"Numéro de série / UID : {port.serial_number}")
        print("----------")

        port_id = port.device
        if port_id not in connected_ports:

            # Teste si le port est ouvert et peut communiquer eviter la diff entre console et usb_cdc.data
            print(f"Test du port : {port_id}")
            if try_handshake(port_id):
                ser = safe_open(port_id)
                if ser:
                    connected_ports[port_id] = ser
                    print(f"[✓] Plateau connecté sur {port_id}")
                    new_feathers.append(ser)

    return new_feathers

    

"""ports = detect_devices()
if ports:
    port1 = safe_open(ports[0])
    port2 = safe_open(ports[1]) if len(ports) > 1 else None
"""
port1 = None
port2 = None


""" 
# Test automatique des ports
port_detected_1 = get_port_by_serial("4657A1084E384B53202020522D4316FF",ports)  # UID du plateau 1
#port_detected_2 = get_port_by_serial("ICIMETTRELUIDDUPLATEAU2",ports)  # UID du plateau 2 (à remplacer par le vrai UID)

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
"""



def game_ready(port_plateau_1):#, port_plateau_2):
    """
    Attend que les 2 plateaux soit dans le mode duo.
    """
    p1_duo_activated = False
    #p2_duo_activated = False

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
# Voir github commit du 04/23/25


while True:

    check_connections() # Check si y'as pas un plateau qui se barre
    detect_devices() # Détecte les nouveau plateau avant de commencé la partie

    if len(connected_ports) == 1:
        print("[1] Un seul plateau détecté. En attente du second...\n")

    if len(connected_ports) >= 2:
        ports_list = list(connected_ports.values())
        print("[2] Deux plateaux connectés ! Lancement de la partie...\n")

   
        game_ready(ports_list[0], ports_list[1])
       

    time.sleep(2)