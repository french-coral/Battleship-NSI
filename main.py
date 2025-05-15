import serial.tools.list_ports
import time
import random

connected_ports = {} # UID : serial.Serial object
                    
                     # UID Supposé : 6E9E13C44E384B53202020521E2216FF &  657A1084E384B53202020522D4316FF


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
    Plateau 2: 6E9E13C44E384B53202020521E2216FF
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
            time.sleep(0.1) # laisse la Feather respirer

            ser.reset_input_buffer() # Soit disant plus clean mais ca pete tout
            ser.reset_output_buffer()

            print("Pinging ...\n")
            ser.write(b"PING\n")  # Commande bidon qui attend une réponse connue (ok)
            ser.flush()
            time.sleep(0.3)

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
    Vérifie si les ports sont toujours actifs et connectés.
    Nettoie proprement si un port est mort, mais attend un peu après une déconnexion massive pour éviter un mental breakdown de la raspberry (elle est trop conne).

    En gros si un port est déco / changer, on le recheck quand même pour être sur qu'il soit vraiment déconnecté et non juste un bus USB linux de merde qui bouge.
    """

    to_remove = []

    for port_name, ser in connected_ports.items():
        try:
            ser.in_waiting  # Simple test léger pour voir si le port est vivant
        except Exception as e:
            print(f"[X] Plateau déconnecté ({port_name}) : {e}")
            to_remove.append(port_name)

    if to_remove:
        print("[INFO] Détection de déconnexion USB - Pause pour stabiliser...")
        time.sleep(2)  # << PAUSE pour laisser Linux rescanner tous les ports (c'est une attente vraiment chiante mais nécessaire)
        for port_name in to_remove:
            try:
                connected_ports[port_name].close()
            except:
                pass
            del connected_ports[port_name]

def detect_devices(baud=9600, timeout=1):
    """
    Détecte les plateaux branché sur les ports USB de la machine (PC ou raspberry pi).
    Envoie un PING et attend une reponse, oh OK il renvoie un accusé de réception pour s'assurer que
    les 2 parties (plateau et script maître) confirme la conection à l'autre.

    Il skip : - Les ports bluetooth qui attendent dans le vide une réponse
              - Les ports déjà connectés  

    Testing purposes : Affiche l'etat des ports dispos
    La FeatherM4 devrait ressembler à ca:
    ----------
    Nom du port     : COMx sous Windows et /dev/ttyACMx sous Linux
    Description     : Périphérique série USB (Port de communiquation)
    Fabricant       : Adafruit
    Produit         : None
    Numéro de série : 4657A1084E384B53202020522D4316FF ou 6E9E13C44E384B53202020521E2216FF
    ----------
   
    """

    ports = serial.tools.list_ports.comports()
    feather_ports = []
    
    for port in ports:
         # Skip les ports Bluetooth connus (ils ouvrent mais n'envoie rien c'est chiant)
        if "Bluetooth" in port.description or "Bluetooth" in port.device:
            #print(f"[IGNORÉ] Port Bluetooth détecté : {port.device}\n")
            continue
        
        #Skip les ports déjà connectés (c plus bo pour la console)
        if port.device in connected_ports:
            print(f"[IGNORÉ] Port déjà connecté : {port.device}\n")
            continue
            
        print("----------")
        print(f"Nom du port     : {port.device}")
        #print(f"Description     : {port.description}")
        #print(f"Fabricant       : {port.manufacturer}")
        #print(f"Produit         : {port.product}")
        print(f"Numéro de série / UID : {port.serial_number}")
        print("----------")

        try:
            # Attend un peu que CircuitPython finisse de redémarrer
            time.sleep(0.5)

            # Utilise TA FONCTION EXISTANTE handshake() pour checker
            if try_handshake(port.device):
                ser = safe_open(port.device)
                if ser:
                    connected_ports[port.device] = ser
                    feather_ports.append(port.device)
                    print(f"[✓] Plateau connecté sur {port.device}")
        except Exception as e:
            print(f"[!] Erreur lors de la tentative de handshake sur {port.device} : {e}")

    return feather_ports


def game_ready(port_plateau_1, port_plateau_2):
    """
    Attend que les 2 plateaux soit dans le mode duo (est cliqué sur l'icon du mode duo).
    """
    p1_duo_activated = False
    p2_duo_activated = False

    while not p1_duo_activated or not p2_duo_activated:

        time.sleep(0.1)

        if not p1_duo_activated: # Evite de checker un truc déjà True
            if port_plateau_1:
                response_p1 = lire(port_plateau_1)
                if response_p1 == "DUOREADY":
                    p1_duo_activated = True
                elif response_p1 == "WENT_SOLO": # Si un plateau va solo l'autre risque d'être bloqué sur le mode duo
                    print(f"Plateau 1 Went Solo")
                    envoyer(port_plateau_2,"DUO_OFF")


        if not p2_duo_activated:
            if port_plateau_2:
                response_p2 = lire(port_plateau_2)
                if response_p2 == "DUOREADY":
                    p2_duo_activated = True
                elif response_p2 == "WENT_SOLO":
                    print(f"Plateau 2 Went Solo")
                    envoyer(port_plateau_1,"DUO_OFF")

    print("Mode duo activé pour les deux plateaux.\n")
    print("Demande de placement des plateaux.\n")
    start_game(port_plateau_1, port_plateau_2)


def start_game(port_plateau_1, port_plateau_2):
    """
    Fonction principale pour démarrer le jeu.
    Placement des bateaux, attente de la préparation des joueurs,
    """

    global game_running

    # Phase de placement des bateaux
    envoyer(port_plateau_1, "PLACE")
    envoyer(port_plateau_2, "PLACE")

    # Attente du placement des 2 plateaux
    ready1 = False
    ready2 = False
    boats1 = None
    boats2 = None

    print("[INFO] Phase de placement démarrée.")

    while not (ready1 and ready2 and boats1 and boats2):
        # Lecture plateau 1
        cmd1 = lire(port_plateau_1)
        if cmd1:
            if cmd1 == "READY":
                ready1 = True
                print("[✓] Joueur 1 prêt.")
            elif cmd1.startswith("BOATS:"):
                boats1 = cmd1
                print("[INFO] Bateaux du joueur 1 reçus.")

        # Lecture plateau 2
        cmd2 = lire(port_plateau_2)
        if cmd2:
            if cmd2 == "READY":
                ready2 = True
                print("[✓] Joueur 2 prêt.")
            elif cmd2.startswith("BOATS:"):
                boats2 = cmd2
                print("[INFO] Bateaux du joueur 2 reçus.")

        time.sleep(0.05)  # Petite pause pour ne pas surcharger la CPU inutilement

    print("[INFO] Les deux joueurs sont prêts et les bateaux sont reçus.")
    
    # Une fois les deux prêts et les bateaux récupérés :
    envoyer(port_plateau_1, boats2)  # J1 reçoit les bateaux de J2
    envoyer(port_plateau_2, boats1)  # J2 reçoit les bateaux de J1
    print("[✓] Bateaux envoyés aux deux joueurs.")

    time.sleep(0.5)  # Le temps que les messages arrivent tranquillement

    game_running = True
    game_loop(port_plateau_1, port_plateau_2)

def game_loop(port_plateau_1, port_plateau_2):

    nom = ['Joueur 1', 'Joueur 2']
    joueur_actuel = 0

    def attendre_reponse(port):
        """
        Attend indéfiniment une réponse du joueur.
        """
        while True:
            cmd = lire(port)
            if cmd:
                return cmd
            time.sleep(0.1)  # petite pause pour ne pas surcharger le CPU

    while True:
        print(f"\n---- TOUR du {nom[joueur_actuel]} ----")

        if joueur_actuel == 0:
            envoyer(port_plateau_1, "YOURTURN")
            cmd = attendre_reponse(port_plateau_1)

            if cmd.startswith("TIR:"): # On envoie le tir réalisé pour avoir une réponse.
                envoyer(port_plateau_2, cmd)
            
            elif cmd == "LOSE":
                print("WIN du joueur 2")
                envoyer(port_plateau_2,"VICTOIRE")
                time.sleep(1)
                break

            joueur_actuel = 1

        else:
            envoyer(port_plateau_2, "YOURTURN")
            cmd = attendre_reponse(port_plateau_2)

            if cmd.startswith("TIR:"):
                envoyer(port_plateau_1, cmd)

            elif cmd == "LOSE":
                print("WIN du joueur 1")
                envoyer(port_plateau_1,"VICTOIRE")
                time.sleep(1)
                break

            joueur_actuel = 0

    print("Partie terminée.")


# Boucle principale du 1v1 p1 et p2 à remplacer part port_plateau_1 et port_plateau_2
# Voir github commit du 23/04/25
# Most likely outdated as possible

    
#Set up les ports
port1 = None
port2 = None

print("[INFO] Main script lunched")

while True:

    check_connections() # Check si y'as pas un plateau qui se barre
    detect_devices() # Détecte les nouveau plateau avant de commencé la partie

    # On veut 2 plateaux fonctionnels avant de démarrer
    if len(connected_ports) < 2:
        print(f"[WAIT] Plateaux connectés : {len(connected_ports)}. En attente de 2 plateaux...\n")
        time.sleep(2)
        continue

    ports_list = list(connected_ports.values()) # Num serial des plateaux connectés

    # Assurer que les 2 ports sont toujours accessibles
    try:
        if ports_list[0].is_open and ports_list[1].is_open:
            print("[✓] Deux plateaux actifs détectés. Lancement du jeu.\n")
            game_ready(ports_list[0], ports_list[1])
        else:
            print("[X] Un port est fermé. Réinitialisation en attente.")
            time.sleep(2)
            continue

    except Exception as e:
        print(f"[ERROR] Erreur en vérifiant les ports : {e}")
        time.sleep(2)
        continue

    # Après la partie (quand game_ready + game_loop sont finis), on recommence depuis zéro
    print("[INFO] Partie terminée. Reset des connexions.\n")

    # Ferme proprement tout ce qui était utilisé
    for ser in ports_list:
        try:
            ser.close()
        except:
            pass
    connected_ports.clear()
    time.sleep(2)  # Petite pause avant de redétecter