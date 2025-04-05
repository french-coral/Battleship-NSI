import serial.tools.list_ports

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
    
port_plateau_1 = safe_open(get_port_by_serial("4657A1084E384B53202020522D4316FF")) # UID du plateau 1, voir boot_out.txt dans CIRCUITPY(D:)
#port_plateau_2 = get_port_by_serial("ICIMETTRELUIDDUPLATEAU2")

if port_plateau_1:
    ser1 = serial.Serial(port_plateau_1, 9600, timeout=1)
    print("Plateau 1 connecté.")
#if port_plateau_2:
    #ser2 = serial.Serial(port_plateau_2, 9600, timeout=1)
    #print("Plateau 2 connecté.")
else:
    print("Aucun plateau connecté.")

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
    # lire_message(ser): ser étant le plateau
    # envoyer(ser,message): ser étant le plateau et message le message à envoyer
    
###########################################################################

def lire_message(ser):
    if ser.in_waiting:
        msg = ser.readline().decode().strip()
        print("Reçu :", msg)
        return msg
    return None

def envoyer(ser, message):
    ser.write((message + "\n").encode())
    print("Envoyé :", message)

while True:
    """
    Boucle principale du jeu.
    Pour le moment test solo.
    """
    msg1 = lire_message(ser1) # msg du plateau_1
    if msg1:
        if msg1.startswith("PLACEMENT") or msg1.startswith("TIR"):
            coord = msg1.split(":")[1]
            x, y = map(int, coord.split(","))
            print(f"Action sur plateau 1 : x={x}, y={y}")
            # Ex: test réponse
            envoyer(ser1, f"LED:{x},{y},green")


