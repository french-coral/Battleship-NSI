import time
import board
import usb_cdc
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

    def handle_button(self, x, y, edge):
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

    def initialize_board(self):
        """
        Initialisation des LEDs avec un effet dégradé, miam miam
        """
        for y in range(8):
            for x in range(8):
                self.trellis.activate_key(x, y, NeoTrellis.EDGE_RISING)
                self.trellis.set_callback(x, y, self.handle_button) # associe la fonction handle quand le (x,y) est cliqué

                # Applique un dégradé
                gradient_color = (x * 32, y * 32, 150)
                self.set_led(x, y, gradient_color)
                time.sleep(0.05)

        # Éteint toutes les LEDs après l'effet de démarrage
        time.sleep(0.5)
        for y in range(8):
            for x in range(8):
                self.set_led(x, y, OFF)
                time.sleep(0.02)

    def benchmark(self,x,y):
        if self.get_led_status(x,y) != OFF:
            self.set_led(x,y,OFF)

        self.set_led(x,y,MAGENTA)

    def menu(self):
        """
        Set les leds et bouttons du menu en fonction du menu_type
        solo: I
        duo: I et II
        """
        if mode == 'PVE':
            menu_type = 'Solo'
            leds_ = [(1,1),(1,2),(5,1),(5,2),(6,1),(6,2)] # le I du menu
            for i in range(2):
                self.set_led(leds_[i][0],leds_[i][1],BLUE)
            for n in range(2,6):
                self.set_led(leds_[n][0],leds_[n][1],RED)
        else:
            menu_type = 'Duo'
            leds_ = [(1,1),(1,2),(5,1),(5,2),(6,1),(6,2)] # le I et le II du menu
            for i in range(6):
                self.set_led(leds_[i][0],leds_[i][1],BLUE)


# Création et initialisation du gestionnaire
manager = TrellisManager(trellis)
manager.initialize_board()
manager.menu()

#manager.benchmark(0,1)

# Boucle principale
while True:
    trellis.sync()  # Met à jour les événements des boutons
    time.sleep(0.01)


