import time
import board
import usb_cdc
import random
from adafruit_neotrellis.neotrellis import NeoTrellis
from adafruit_neotrellis.multitrellis import MultiTrellis


uart = usb_cdc.data if usb_cdc.data else None #Evite le None que je sais pas pourquoi c'est là

# Temps d'attente avant de passer en mode autonome
TIMEOUT_USB = 3

def detect_mode():
    """Détecte si la Feather est branchée à un PC ou juste à l’alimentation."""
    if not uart:  # Si usb_cdc.data est None, pas de mode 1v1
        return "PVE"

    start_time = time.monotonic()
    while time.monotonic() - start_time < TIMEOUT_USB:
        if uart.in_waiting:  # Si on reçoit une donnée, on est connecté au PC
            return "1v1"

    return "PVE"  # Si rien reçu après le timeout, mode autonome

# Détection au démarrage
mode = detect_mode()
print(f"Mode détecté: {mode}")

if mode == "1v1":
    print("Mode 1v1 activé (PC/raspberry connecté)")
    uart.write(b"MODE 1v1\n")
else:
    print("Mode PVE activé (aucune connexion USB)")


# Init du I2C
i2c_bus = board.I2C()

#modules NeoTrellis
trelli = [
    [NeoTrellis(i2c_bus, False, addr=0x2E), NeoTrellis(i2c_bus, False, addr=0x2F)],
    [NeoTrellis(i2c_bus, False, addr=0x30), NeoTrellis(i2c_bus, False, addr=0x31)],
]
trellis = MultiTrellis(trelli) #Gestion pour le 8x8

#couleurs
OFF = (0, 0, 0)
BLUE = (0, 150, 250)
MAGENTA = (255, 0, 255)
RED = (255, 0, 0)

class TrellisManager:
    def __init__(self, trellis):
        self.trellis = trellis
        self.led_status = [[OFF for i in range(8)] for i in range(8)]  # Stockage de l'état des LEDs dans une matrice

    def get_led_id(self, x, y):
        """
        Convertit les coord en un ID de la LED
        coord: (x,y)
        ID: (0-63)
        """
        return y * 8 + x

    def get_led_coordinates(self, led_id):
        """
        Convertit un ID LED en coordonnées
        coord: (x,y)
        ID: (0-63)
        """
        return led_id % 8, led_id // 8

    def set_led(self, x, y, color):
        """
        Change la couleur d'une LED et met à jour son état
        coord: (x,y)
        color: obvious
        """
        self.led_status[y][x] = color
        self.trellis.color(x, y, color)

    def get_led_status(self, x, y):
        """
        Récupère l'état actuel d'une LED d'après ses coord
        coord: (x,y)
        """
        return self.led_status[y][x]

    def handle_button_test(self, x, y, edge):
        """
        Gère les appuis sur les boutons
        coord: (x,y)
        edge: RISING ou FALLING
        """
        if edge == NeoTrellis.EDGE_RISING:# Button qui remonte
            if self.get_led_status(x, y) == OFF:
                self.set_led(x, y, BLUE)  # Bleu
            else:
                self.set_led(x, y, OFF)   # Éteint si déjà allumé

    def initialize_board(self,step:str):
        """
        Initialisation des LEDs avec un effet dégradé, miam miam
        """
        if step == "menu":
            couleur_gradient = 5
        else: #Current else : "init"
            couleur_gradient = 32


        for y in range(8):
            for x in range(8):
                self.trellis.activate_key(x, y, NeoTrellis.EDGE_RISING)
                self.trellis.set_callback(x, y, self.handle_button_test) # associe la fonction handle quand le (x,y) est cliqué

                # Applique un dégradé
                gradient_color = (x * couleur_gradient, y * couleur_gradient, 150)
                self.set_led(x, y, gradient_color)
                time.sleep(0.01)

        # Éteint toutes les LEDs après l'effet de démarrage
        time.sleep(0.05)
        for y in range(8):
            for x in range(8):
                self.set_led(x, y, OFF)
                time.sleep(0.01)

    def benchmark(self,x,y):
        """Benchmark temp pour mapper le board"""
        if self.get_led_status(x,y) != OFF:
            self.set_led(x,y,OFF)

        self.set_led(x,y,MAGENTA)

    def handle_menu(self, x, y, edge):
        """
        Gère le choix du menu en fonction du bouton pressé
        """
        if edge == NeoTrellis.EDGE_RISING:
            if (x, y) in [(1,1), (1,2)]:  # Si on appuie sur la partie "Solo"
                self.menu_type = 'Solo'
                self.initialize_board("menu")
                self.solo_start()
            elif (x, y) in [(5,1), (5,2), (6,1), (6,2)]:  # Si on appuie sur "Duo"
                self.menu_type = 'Duo'
            print(f"Mode sélectionné : {self.menu_type}")


    def placer_bateaux(self):
        """
        Place aléatoirement 3 bateaux sur la grille.
        Retourne une liste de tuples représentant avec positions des bateaux.
        """
        grille = [[0] * 8 for n in range(8)]  # Grille vide 8x8 (0 = libre ; 1 = occupé)
        tailles_bateaux = [4, 3, 2]  # (Grand, Moyen, Petit)
        bateaux_places = []  # Liste des bateaux avec leurs positions

        for taille in tailles_bateaux:
            IsBateau_placed = False

            while not IsBateau_placed:
                x = random.randint(0, 7)
                y = random.randint(0, 7)
                direction = random.choice(["H", "V"])  # Horizontal ou Vertical en gros


                # Vérifier si le bateau peut être placé
                positions = []
                if direction == "H" and x + taille <= 8:  # Horizontal touche t il le bord ?
                    for i in range(taille):
                        positions.append((x + i, y))# Pose horizontal
                elif direction == "V" and y + taille <= 8:  # Vertical, même chose
                    for i in range(taille):
                        positions.append((x, y + i))# Pose vertical

                if not positions: # si le bateau depasse du plateau on retry
                    continue

                IsBateau_placable = True
                for x,y in positions:
                    if grille[x][y] == 1: # déjà occupé
                        IsBateau_placable = False
                        break
                if IsBateau_placable:
                    for x, y in positions:
                        grille[x][y] = 1
                    bateaux_places.append(positions)# enregistre les coordonnées valides
                    IsBateau_placed = True

        return bateaux_places

    def solo_start(self):
        bots_bateaux = self.placer_bateaux()
        for bateau in bots_bateaux:
            print(bateau)  # Affiche les coordonnées des bateaux choisi par le bot



    def menu(self):
        """
            Set les leds et bouttons du menu en fonction du  type de menu
            solo: I
            duo: I et II (sur le menu)
        """
        leds_ = [(1,1),(1,2),(5,1),(5,2),(6,1),(6,2)]  # Boutons du menu
        if mode == 'PVE':
            for i in range(2):
                self.set_led(leds_[i][0],leds_[i][1], BLUE)
                self.trellis.activate_key(leds_[i][0], leds_[i][1], NeoTrellis.EDGE_RISING)
                self.trellis.set_callback(leds_[i][0], leds_[i][1], self.handle_menu)
            for n in range(2,6):
                self.set_led(leds_[n][0],leds_[n][1], RED) #Pas dispo
        else:
            for i in range(6):
                self.set_led(leds_[i][0],leds_[i][1], BLUE)
                self.trellis.activate_key(leds_[i][0], leds_[i][1], NeoTrellis.EDGE_RISING)
                self.trellis.set_callback(leds_[i][0], leds_[i][1], self.handle_menu)

# Création et initialisation du gestionnaire
manager = TrellisManager(trellis)
manager.initialize_board("init")
manager.menu()

#manager.benchmark(0,1)

# Boucle principale
while True:
    trellis.sync()  # Met à jour les événements des boutons
    time.sleep(0.01)


