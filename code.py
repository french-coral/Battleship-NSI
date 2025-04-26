"""
################################################################################################################

Les commentaires présents le long de ce code n' ont pas été corrigé ou vérifié en détails, il se peut qu'un certain "franglais"
s'y glisse, je m'en excuse. (c'est pour moi de base)
De plus certains commentaire sont outdated (si besoin il y a des dates sur certains commentaires)

J'espère être le plus claire possible. Bonne chance. (vous en aurez besoin)
En cas de question spécifique et TRES technique demandé à : Noah (il connait bien le code)

################################################################################################################

Informations sur le code / jeu :
- Le jeu est un jeu de 2 joueurs (Bataille Navale).
- Le plateau est un 8x8.
- Tour par tour.
  - Si un joueur (bot ou joueur) touche un bateau il rejoue.

- Chaque joueur a une flotte de 3 navires : Grand => 4 cases / Moyen => 3 cases /Petit => 2 cases
- Le joueur doit choisir la position de ses navires sur le plateau.
  - Si le placement débuté ne convient pas il peut reappuyer sur les cases indésiré ou simplement cliqué ailleurs (qui ne fait pas suite du bateau)
- Le bot a ses navires positionnés automatiquement sur le plateau.

- Menu avec "Solo" et "Duo" mode.  // D'autres jeu seront peut-être ajoutez
  - Un mode solo est disponible, il est codé sur le plateau directement.
  - Le mode duo est disponible seulement si branché à la rapberry (finalité, pour le moment sur le pc, voir main.py)
  - Le mode duo est disponible seulement si les 2 plateaux sont branchés. (dans la théorie)

Fonctionnement du mode 1v1 / Duo :
- Le script maître attent que les 2 plateaux est séléctionnés le mode duo via le menu
- Le script maître demande au 2 plateaux de placer leur bateaux respectifs : quand c'est fait les 2 renvoire READY
- Puis le script maître gère simplement le transfert d'information et la logique de tour.
- Les leds , logique de jeu, placement de bateaux, touché coule etc sont gérer respectivement sur chacun des plateaux

- Le transfert de données / infos se fait par l'ouverture des port par leur UID (cd boot_out.txt dans le (E:)CIRCUITPY)
- Les données / infos passe ensuite par usb_cdc.data (faire la dif avec usb_cdc.console)
  - Les données sont des chaînes de caractères encodées en 8bits
- Le plateau ne décode rien de ce sui concerne la partie il fait juste le transfert d'une carte à l'autre.


################################################################################################################

"""

import time
import board
import usb_cdc
import random
from adafruit_neotrellis.neotrellis import NeoTrellis
from adafruit_neotrellis.multitrellis import MultiTrellis


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
BLUE = (0, 150, 250) # Vue des bateaux (placement et instance attaqué)
GREEN = (0,255,0) # Placement des bateaux et animation de win
FIN_COLOR = None # Pour les animation de fin de solo mode
MAGENTA = (255, 0, 255) # Complétement inutile
RED = (255, 0, 0) # Tir raté ou placement invalide + animation de loose
GRAY = (100, 100, 100)  # Gris pour les tirs ratés du bot
ORANGE = (255, 165, 0)  # Orange pour les tirs qui touchent un bateau
blink_bots_play = 0.1 # Temps de clignotement des LEDs du bot pour vois où il a tiré
couleurs_bateaux = [(0, 0, 255), (0, 128, 255), (0, 255, 255)]  # Bleu foncé, bleu moyen, bleu clair # Teintes de bleu pour chaque bateau (Request de Noah)


#############################################

# Les fonctions suivantes sont à usage unique pour l'init de connection, seulement pour set up le mode PVE ou 1V1

#############################################


def waiting_animation():
    """
    Toujours maintenir l'attention
    """
    for i in range(2):
        trellis.color(3, 3, GREEN)
        trellis.color(3, 4, OFF)
        time.sleep(0.2)
        trellis.color(4, 3, GREEN)
        trellis.color(3, 3, OFF)
        time.sleep(0.2)
        trellis.color(4, 4, GREEN)
        trellis.color(4, 3, OFF)
        time.sleep(0.2)
        trellis.color(3, 4, GREEN)
        trellis.color(4, 4, OFF)
        time.sleep(0.2)
    trellis.color(3, 4, OFF)


# Serial / absolument useless mtn 23/04
def wait_for_connection():
    """
    Attend l'arrivée de la connection

    Edit: Ne marche pas du tout 06/04

    """
    timeout = 0
    waiting_animation()
    while usb_cdc.data is None:
        print("Attente de la connexion USB CDC...")
        timeout += 1
        if timeout > 5:
            print("Erreur de connexion USB CDC")
            return
        time.sleep(0.3)

def detect_mode(): #Fonction ne sert nul part mais quand je l'enlève ca casse, donc ca reste là pour le moment
    """
    Détecte si le plateau est connecté à un script maître (pc ou raspberry) via USB.

    Edit: - Fonction originale vouer à changer. 06/04
          - Maintenant seulement basé sur la com usb_cdc.data et non un vrai échange pour être sur de la disponibilité du plateau. 09/04
          - Enfait usb_cdc.data EST ouvert c'est juste que y'as pas forcement quelqu'un qui y accède, en gros ca check juste si le plateau est branché en USB
            si le mode PVE s'active c'est que c'est vraiment la merde, gl. 23/04
    """
    # /!/ Si vous utliser cette ligne en dessous n'oubliez pas d'ajouter 'import supervisor' /!/
    # Alternative en test pour le check de com. renvoie True : je travail encore dessus 
    # if supervisor.runtime.serial_connected: 
    #    return "1v1"

    if communication:
        
        return "1v1"
    return "PVE"


communication = usb_cdc.data

def lire():
    """
    Récupère les messages via USB et les sépare si plusieurs messages sont collés. (pb au deboggage)
    Il existe un version bien plus simple cependant elle est là pour faire des tests (restera peut être à la fin du projet)
    """
    if communication.in_waiting:
        try:
            return communication.readline().decode().strip()
        except Exception as exept:
            print(f"Erreur lecture : {exept}")
    return None

def envoyer(message):
    """
    Envoie un message via USB.
    """
    try:
        communication.write((message + "\n").encode())
        communication.flush()
    except Exception as e:
        print("Erreur d'envoi :", e)


def attendre_handshake():
    """
    Attente du handshake pour initialisé la communication feather-server
    """
    print("En attente d'un PING pour initialisation...")

    communication.reset_input_buffer()
    tries = 0
        
    while True and tries < 3000:
        cmd = lire()
        tries += 0.01
        if cmd == "PING":
            print(f">>> {cmd}")
            envoyer("OK")
            print("Réponse envoyée : OK")
            print("Waiting for recepetion ...")
            
        elif cmd == "RECEIVED":
            print(f">>> {cmd}")
            print("Réponse reçue, handshake terminé.\n")
            break

    if cmd != "RECEIVED":
        print("[x] End of handshake\n")
        return "PVE"

    return "1V1"

#############################################

# Fin d'init du mode de jeu

#############################################

class TrellisManager:
    def __init__(self, trellis):
        self.trellis = trellis
        self.led_status = [[OFF for i in range(8)] for i in range(8)]  # Stockage de l'état des LEDs dans une matrice

    def get_led_id(self, x, y):
        """
        Convertit les coord en un ID de la LED, pas utiliser vraiment, plus pour du débug si besoin
        coord: (x,y)
        ID: (0-63)
        """
        return y * 8 + x

    def get_led_coordinates(self, led_id):
        """
        Convertit un ID LED en coordonnées, comme préciser dans get_led_id(), cette fonction à pour but de débug et mapper le tableau,
        ce n'est pas utilisé.
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
        Plus c'est le bac à sable du menu. C'est cool, on le garde
        coord: (x,y)
        edge: RISING ou FALLING
        """
        if edge == NeoTrellis.EDGE_RISING:# Button qui remonte
            if self.get_led_status(x, y) == OFF:
                self.set_led(x, y, (random.randint(0,255),random.randint(0,255),random.randint(0,255)))  # Color random c bo 
            else:
                self.set_led(x, y, OFF)# Éteint si déjà allumé
            envoyer('OK')

    def blink(self,x,y,color,init_color = None, time_blink = 0.05):

        if not init_color: init_color = self.get_led_status(x, y) # Si pas préciser ca prend tout seul la couleur de base de la touche

        repeat = 4 # Blink error placement (lors du placement des bateaux)
        if time_blink is blink_bots_play:
            repeat = 2 # Blink tire bot (pour voir distinctment le coup du bot)

        for i in range(repeat):
            self.set_led(x,y,color)
            time.sleep(time_blink)
            self.set_led(x,y,OFF)
            time.sleep(time_blink)

        self.set_led(x,y,init_color) # Return to original state

    def initialize_board(self,step:str):
        """
        Initialisation des LEDs avec un effet dégradé, miam miam

        Le but est l'animation du board qui ce clear donc la couleur dépend du "couleur_gradient",
        plus il est élevé plus la différence des couleurs du dégradé seront marquées.

        Animations (step):
        - "Menu" = blue / light blue
        - "endGame_Win" = Green victory animation + multi-pastel colors clear animation
        - "endGame_Lose" = Red victory animation + multi-pastel colors clear animation
        - "init" = Initialisation du plateau

        """
        if step == "menu":
            couleur_gradient = 5
        elif step == "endGame_Win" or step == "endGame_Lose":
            couleur_gradient = 150
        else: # Current else : "init"
            couleur_gradient = 32


        if couleur_gradient == 150 : # End animation
            if step == "endGame_Win": FIN_COLOR = GREEN
            else: FIN_COLOR = RED
            for r in range(3):
                for i in range(8):
                    for j in range(8):
                        self.set_led(i, j, FIN_COLOR)
                for i in range(8):
                    for j in range(8):
                        self.set_led(i, j, OFF)

        # Bac à sable du menu, il est un peu perdu mais oklm
        for y in range(8):
            for x in range(8):
                self.trellis.activate_key(x, y, NeoTrellis.EDGE_RISING)
                self.trellis.set_callback(x, y, self.handle_button_test) # associe la fonction handle quand le (x,y) est cliqué. ps: si question sur le callback demander à Matteo ;)

                # Applique un dégradé
                gradient_color = (x * couleur_gradient, y * couleur_gradient, 150)
                self.set_led(x, y, gradient_color)
                time.sleep(0.02)


        # Configure le bouton de reset (ne marche visiblement pas donc on va le comment out temporairement)
        # Marchera probablement jamais. 09/04
        #self.trellis.activate_key(0, 0, NeoTrellis.EDGE_RISING)
        #self.trellis.activate_key(0, 0, NeoTrellis.EDGE_FALLING)
        #self.trellis.set_callback(0, 0, self.benchmark_reset)


        # Éteint toutes les LEDs après l'effet de clear/demarrage
        time.sleep(0.05)
        for y in range(8):
            for x in range(8):
                self.set_led(x, y, OFF)
                time.sleep(0.01)

    def benchmark_reset(self, x, y, edge):
        """
        Fonction de "RESET" : Réinitialise le plateau si un bouton est maintenu plus de 2,5 secondes.

        Edit: - Ne marche absolument pas, besoin d'une alternative.  04/04
              - Débrancher - rebrancher fera l'affaire parce que c'est infaisable comme feature.  09/4

        """
        reset_button = (0, 0)  # Coordonnées du bouton de reset
        hold_time = 2.5  # Temps nécessaire pour déclencher le reset (secondes)

        if (x, y) == reset_button:  # Vérifie si le bouton de reset est pressé
            if edge == NeoTrellis.EDGE_RISING:  # Début de l'appui
                self.reset_start_time = time.monotonic()  # Enregistre le temps de début de l'appui
            elif edge == NeoTrellis.EDGE_FALLING:  # Fin de l'appui
                if time.monotonic() - self.reset_start_time >= hold_time:  # Vérifie la durée de l'appui
                    print("//RESET//\n")
                    print("... ... ...\n")  # Pour bien paniquer :)
                    self.reset_requested = True
                    self.game_running = False  # Arrête la partie en cours
                    self.bot_attacking = False
                    self.bot_attacked = False
                    self.player_turn = False
                    self.bot_sunken_ships = []
                    self.current_bot_sunken_ships = []
                    self.player_grid = [[0] * 8 for _ in range(8)]
                    self.bot_grid = [[0] * 8 for _ in range(8)]
                    self.bot_last_hit = None
                    self.bot_targets = []

                    # Réinitialise le plateau et retourne au menu
                    self.initialize_board("init")
                    self.menu()
    
    def clear_all_callbacks(self):
        """
        Clear all callbacks des bouttons.

        """
        for y in range(8):
            for x in range(8):
                self.trellis.set_callback(x, y, None)
    
    def menu(self):
            """
                Set les leds et bouttons du menu en fonction du  type de menu
                Solo: I
                Duo: I et II (sur le menu)

                Edit : Vouer à être modifier avec le mode duo gérer sur raspberry.  03/04

            """
            mode = attendre_handshake()


            print("Affichage du menu...")
            print(f"Mode détecté : {mode}")

            self.trellis.activate_key(6, 6, NeoTrellis.EDGE_RISING)
            self.trellis.set_callback(6, 6, self.handle_menu)

            leds_ = [(1,1),(1,2),(5,1),(5,2),(6,1),(6,2)]  # Boutons du menu
            if mode == 'PVE':
                for i in range(2):
                    self.set_led(leds_[i][0],leds_[i][1], BLUE)
                    self.trellis.activate_key(leds_[i][0], leds_[i][1], NeoTrellis.EDGE_RISING)
                    self.trellis.set_callback(leds_[i][0], leds_[i][1], self.handle_menu)
                for n in range(2,6):
                    self.set_led(leds_[n][0],leds_[n][1], RED) #Mode de jeu pas dispo donc rouge

            else: # Les 2 modes sont disponibles
                for i in range(6):
                    self.set_led(leds_[i][0],leds_[i][1], BLUE)
                    self.trellis.activate_key(leds_[i][0], leds_[i][1], NeoTrellis.EDGE_RISING)
                    self.trellis.set_callback(leds_[i][0], leds_[i][1], self.handle_menu)
            
    def handle_menu(self, x, y, edge):
        """
        Gère le choix du menu en fonction du bouton pressé

        Edit: Sera modifier si déplacer sur raspberry pi.  03/04
              Peut-être pas enfait. 06/04
        """

        if edge == NeoTrellis.EDGE_RISING:
            if (x, y) in [(1,1), (1,2)]:  # Si on appuie sur la partie "Solo"
                self.menu_type = 'Solo'
                self.initialize_board("menu")
                self.main1()


            elif (x, y) in [(5,1), (5,2), (6,1), (6,2)]:  # Si on appuie sur "Duo"
                if mode == 'PVE': # Animation du mode non disponible
                    self.menu_type = 'Solo'
                    self.initialize_board('endGame_Lose') # /Debug/ Animation testing purposes
                    self.menu()
                else:
                    self.menu_type = 'Duo'
                    self.initialize_board("menu")
                    self.envoyer("DUOREADY")
                    self.main2()

            elif (x, y) in [(6,6)]:  # Si on appuie sur "KubeKube"
                print("Mode KubeKube sélectionné")
                self.menu_type = 'KubeKube'
                self.initialize_board("menu")
                self.start_kube()

            # if self.menu_type :print(f"Mode sélectionné : {self.menu_type}") # Trop de fonction et de test renvoyaient les mêmes infos


    #########################################################################################
    ############################ Mode PVE a partir de cette ligne ###########################
    #########################################################################################

    def placer_bateaux_bots(self):
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
                direction = random.choice(["Horz", "Vert"])  # Horizontal ou Vertical en gros


                # Vérifier si le bateau peut être placé
                positions = []
                if direction == "Horz" and x + taille <= 8:  # Horizontal touche t il le bord ?
                    for i in range(taille):
                        positions.append((x + i, y)) # Pose horizontal
                elif direction == "Vert" and y + taille <= 8:  # Vertical, même chose
                    for i in range(taille):
                        positions.append((x, y + i)) # Pose vertical

                if not positions: # si le bateau depasse du plateau on retry jusqu'à que ce rentre
                    continue

                IsBateau_placable = True
                for x,y in positions:
                    if grille[x][y] == 1: # 1 = déjà occupé
                        IsBateau_placable = False
                        break
                if IsBateau_placable:
                    for x, y in positions:
                        grille[x][y] = 1
                    bateaux_places.append(positions) # enregistre les coordonnées valides
                    IsBateau_placed = True

        return bateaux_places

    def placement_bateaux(self):
        """
        Permet au joueur de placer ses propres bateaux.
        Les bateaux sont placés dans l'ordre : Grand (4), Moyen (3), Petit (2).

        Logique :
        - Le joueur sélectionne une première case pour commencer un bateau.
        - La deuxième case détermine la direction (horizontale ou verticale).
        - Les cases suivantes sont ajoutées dans la direction choisie jusqu'à ce que le bateau soit complètement placé.

        - Les cases doivent être adjacentes et alignées dans la direction choisie.
        - Les cases déjà utilisées ou en dehors de la grille ne sont pas valides.
        - Le joueur peut placé devant ou derrière la bateu en cours de placement tant qu'elles sont valides

        """
        tailles_bateaux = [4, 3, 2]  # Tailles des bateaux à placer
        self.player_ships = []  # Réinitialise les bateaux du joueur
        bateau_en_cours = []  # Stocke temporairement les positions du bateau en cours de placement
        direction = None  # Direction du bateau (None, "Horz", "Vert")
        bateau_actuel = 0  # Index du bateau en cours de placement


        def handle_placement(x, y, edge):
            """
            Callback pour gérer le placement des bateaux.
            """
            nonlocal bateau_en_cours, direction, bateau_actuel

            if edge == NeoTrellis.EDGE_RISING:
                # Si le joueur appuie sur une case déjà sélectionnée, annule cette case
                if (x, y) in bateau_en_cours:
                    # Vérifie si la case supprimée est entre deux autres cases
                    bateau_en_cours.remove((x, y))
                    self.set_led(x, y, OFF)  # Éteint la LED

                    # Réinitialise la direction si aucune ou une seule case est sélectionnée
                    if len(bateau_en_cours) < 2:
                        direction = None
                        return

                    # Cas pariculier lors du placement du Grand bateau : je place 3 cases et je supprime celle du milieu, ca fait un bateau fracturé en 2 parties.
                    if len(bateau_en_cours) >= 2: # Si 3 selectioner (uniquement pour le placement du bateau de 4 de long)
                        xs = [coord[0] for coord in bateau_en_cours] # xs = [x1,x2,x3]; x des 3 cases séléctionner
                        ys = [coord[1] for coord in bateau_en_cours] # ys = [y1,y2,y3]; y des 3 cases séléctionner

                        if direction == "Horz" and min(xs) < x < max(xs): # x change si Horz
                            # Si la case supprimée est entre deux cases en direction horizontale
                            for bx, by in bateau_en_cours:
                                self.set_led(bx, by, OFF)
                            bateau_en_cours = []
                            direction = None
                            return
                        elif direction == "Vert" and min(ys) < y < max(ys): # y change si Vert
                            # Si la case supprimée est entre deux cases en direction verticale
                            for bx, by in bateau_en_cours:
                                self.set_led(bx, by, OFF)
                            bateau_en_cours = []
                            direction = None
                            return
                        

                # Empêche de placer un bateau sur un autre bateau.
                for ship in self.player_ships:
                    if (x, y) in ship:
                        self.blink(x, y,RED)
                        return


                print(f'Trying {x,y} in {bateau_en_cours}. Direction: {direction}/ Longueur: {len(bateau_en_cours)}\n') # Debugging


                #################### 1ere case : Init ####################

                # Si aucune case n'a encore été sélectionnée pour ce bateau
                if not bateau_en_cours:
                    bateau_en_cours.append((x, y))
                    self.set_led(x, y, GREEN)  # Marque la première case en vert
                    print(f'Init at {x,y}')
                    return


                ############### 2eme case : init direction ###############

                ##############################################################################
                ##############################################################################

                # Code initiale remplacer, upload github du 04/04/25 si besoin de tester

                # Alternative qui devrait marcher / même logique qu'avant mais plus simple a comprendre

                ##############################################################################
                ##############################################################################

                if len(bateau_en_cours) == 1:
                    x0, y0 = bateau_en_cours[0]

                    #Verification des case adjacentes pour déterminer la direction (horizontale et verticale)
                    if abs(x - x0) == 1 and y == y0:
                        direction = "Horz"
                    elif abs(y - y0) == 1 and x == x0:
                        direction = "Vert"
                    else:
                        # Mauvais clic : reset du placement en cours (tout le bateau est reset) sinon ca fait des coincement de merde impossible à regler
                        print("Mauvaise direction, reset du bateau.")
                        self.blink(x, y, RED, OFF) # Ou GREEN si besoin de l'effet direct
                        for bx, by in bateau_en_cours:
                            self.set_led(bx, by, OFF)
                        bateau_en_cours = []
                        direction = None
                        return


                    bateau_en_cours.append((x, y))
                    self.set_led(x, y, GREEN)  # Marque la deuxième case en vert
                    print(f'2nd case at {x,y} / Direction detected: {direction}')


                ################### 3eme  et 4eme case ###################

                ##############################################################################
                ##############################################################################

                # Le code initial a été remplacé par le code qui suit
                # // Comporte tout le debug initial sur Github //
                # Voir upload Github du 04/04/25 pour avoir une version test qui marche
                # Code revisé et plus simple à lire
                # La logique reste la même, le code originale ne prenait pas le sens de placement mais seulement la direction
                # Le code suivant prend en compte les deux avec le xs et xy basé sur le max du batea_en_cours

                ##############################################################################
                ##############################################################################


                elif direction == "Horz" and len(bateau_en_cours) > 1:

                    print('In Horizontal placement')

                    y_ref = bateau_en_cours[0][1] # Horizontal = même y pour toute les cases

                    xs = [p[0] for p in bateau_en_cours] # Liste des x du bateaux en cours
                    x_head = max(xs) # "Devant" / "tete" du bateau
                    x_tail = min(xs) # "Derrière" / "queue" du bateau

                    if y == y_ref:
                        print(f'x_head :{x_head} / x_tail :{x_tail}')
                        if x == x_head + 1:
                            bateau_en_cours.insert(0, (x, y))
                            self.set_led(x, y, GREEN)
                            print('on head')
                        elif x == x_tail - 1:
                            bateau_en_cours.append((x, y))
                            self.set_led(x, y, GREEN)
                            print('on tail')
                        else:
                            print("Clic hors sujet, pas horizontal = reset.")
                            self.blink(x, y, RED)
                            for bx, by in bateau_en_cours:
                                self.set_led(bx, by, OFF)
                            bateau_en_cours = []
                            direction = None
                            return
                    else:
                        print("Mauvaise ligne pour direction horizontale = reset.")
                        self.blink(x, y, RED)
                        for bx, by in bateau_en_cours:
                            self.set_led(bx, by, OFF)
                        bateau_en_cours = []
                        direction = None
                        return

                elif direction == "Vert" and len(bateau_en_cours) > 1:

                    print('In Vertical placement')

                    x_ref = bateau_en_cours[0][0] # Vertical = même x pour toute les cases

                    ys = [p[1] for p in bateau_en_cours] # Les y du bateau en cours de placement
                    y_head = max(ys)
                    y_tail = min(ys)

                    if x == x_ref:
                        print(f'y_head :{y_head} / x_tail :{y_tail}')
                        if y == y_head + 1:
                            bateau_en_cours.insert(0,(x, y))
                            self.set_led(x, y, GREEN)
                            print('on head')
                        elif y == y_tail - 1:
                            bateau_en_cours.append((x, y))
                            self.set_led(x, y, GREEN)
                            print('on tail')
                        else:
                            print("Clic hors sujet, pas vertical = reset.")
                            self.blink(x, y, RED)
                            for bx, by in bateau_en_cours:
                                self.set_led(bx, by, OFF)
                            bateau_en_cours = []
                            direction = None
                            return
                    else:
                        print("Mauvaise colonne pour direction verticale = reset.")
                        self.blink(x, y, RED)
                        for bx, by in bateau_en_cours:
                            self.set_led(bx, by, OFF)
                        bateau_en_cours = []
                        direction = None
                        return


                # Vérifie si le bateau est complètement placé
                if len(bateau_en_cours) == tailles_bateaux[bateau_actuel]:
                    # Marque le bateau comme placé (bleu)
                    print("//Bateau placé//")
                    for bx, by in bateau_en_cours:
                        self.set_led(bx, by, BLUE)

                    # Ajoute le bateau à la liste des bateaux du joueur
                    self.player_ships.append(bateau_en_cours)
                    print(f"Bateau placé : {bateau_en_cours}")

                    # Passe au bateau suivant
                    bateau_actuel += 1
                    bateau_en_cours = []
                    direction = None

                    # Vérifie si tous les bateaux ont été placés
                    if bateau_actuel == len(tailles_bateaux):
                        print("Tous les bateaux ont été placés.")
                        self.clear_all_callbacks()  # Désactive les callbacks # Désactive les callbacksn. //edit: marche pas comme je voulais
                        return

        # Configure les callbacks pour les boutons
        for y in range(8):
            for x in range(8):
                self.trellis.activate_key(x, y, NeoTrellis.EDGE_RISING)
                self.trellis.set_callback(x, y, handle_placement)

        # Attend que tous les bateaux soient placés
        while len(self.player_ships) < len(tailles_bateaux):
            self.trellis.sync()
            time.sleep(0.01)
        
        # Applique les teintes de bleu aux bateaux une fois placés
        for num_bateau, ship in enumerate(self.player_ships): # Enumerate pour récupérer l'index du bateau et mettre de la couleur
            for gx, gy in ship:
                self.set_led(gx, gy, couleurs_bateaux[num_bateau])  # Applique la couleur en fonction de l'index du bateau

    def display_grid(self, grid, is_player_turn):
        """
        Affiche l'état actuel d'un plateau sur les LEDs.
        grid: Plateau à afficher (player_grid ou bot_grid) en fonction de l'intance (attaquant, attaqué).
        is_player_turn: Booléen indiquant si c'est le tour du joueur.

        """
        for y in range(8):
            for x in range(8):
                if grid[x][y] == 3:  # Bateau touché
                    # Vérifie si le bateau est coulé
                    is_sunk = False # Bateau coulé ?
                    if not is_player_turn: # Dépend de l'intance en court (attaqué, attaquant)
                        ships = self.player_ships
                    else:
                        ships = self.bot_ships

                    for ship in ships:
                        if (x, y) in ship and all(grid[sx][sy] == 3 for sx, sy in ship): # Check si les le bateau touché est censé être coulé. (Est ce que tout les coord du bateau (dans la liste de pos) sont à 3 (touchés) dans la grid)
                            is_sunk = True
                            break
                    if is_sunk:
                        self.set_led(x, y, RED)  # Rouge pour un bateau coulé
                    else:
                        self.set_led(x, y, ORANGE)  # Orange pour un bateau touché mais non coulé
                elif grid[x][y] == 2:  # Bateau non touché
                    if is_player_turn:
                        self.set_led(x, y, OFF)  # Cacher les bateaux du bot au tour du joueur
                    else:
                        # Bleu uniquement sur (player_grid)
                        for num_bateau, ship in enumerate(self.player_ships): # Enumerate pour récupérer l'index du bateau et mettre de la couleur
                            if all(grid[gx][gy] == 3 for gx, gy in ship): 
                                for gx, gy in ship:
                                    self.set_led(gx, gy, RED)
                            else:
                                for gx, gy in ship:
                                    if grid[gx][gy] == 2: # Si le bateau est touché mais pas coulé
                                        self.set_led(gx, gy, couleurs_bateaux[num_bateau])  # Applique la couleur en fonction de l'index du bateau
                    
                elif grid[x][y] == 1:  # Tir raté
                    self.set_led(x, y, GRAY)  # Gris pour un tir raté
                else:  # Case vide
                    self.set_led(x, y, OFF)

    def bot_turn_logic(self):
        """
        Logique pour le tour du bot.

        Logique de la grid:
        0 = Rien
        1 = Tir raté
        2 = Bateau
        3 = Bateau touché

        Edit: Fix les print statement des bateaux coulés (repetition)

        """
        time.sleep(1.5)

        if self.bot_last_hit:  # Si le bot a touché un bateau au dernier tour
            if not self.bot_targets:  # Génère les cases adjacentes à vérifier
                x, y = self.bot_last_hit
                possibles = [(x-1, y), (x+1, y), (x, y-1), (x, y+1)]  # Cases autour du dernier tir

                for i, j in possibles:
                    if 0 <= i < 8 and 0 <= j < 8:  # Vérifie si la case est sur le plateau
                        if self.player_grid[i][j] not in [1, 3]:  # Évite les cases déjà essayées (1 et 3 sont des cases essayées, cf main() docstring )
                            self.bot_targets.append((i, j))

            # Si une direction est déjà déterminée
            if hasattr(self, "bot_direction") and self.bot_direction:  # hasattr(object, 'name"); check si un objet à un attribut spécifique, ici si il existe une direction donner dans la class
                dx, dy = self.bot_direction                                            # self.bot_direction : (1, 0) = Horizontal / (0, 1) = Vertical, quel direction les coordonnées doivent aller ?
                next_x, next_y = self.bot_last_hit[0] + dx, self.bot_last_hit[1] + dy  # Ajoute l'offset en fonction de la direction déterminé

                if 0 <= next_x < 8 and 0 <= next_y < 8 and self.player_grid[next_x][next_y] not in [1, 3]:  # Regarde si l'offset est dans le plateau
                    tir = (next_x, next_y)
                else:
                    # Si la direction échoue, inverse la direction
                    self.bot_direction = (-dx, -dy) # (1,0) => (-1, 0) on va chercher l'autre bout du bateau, e.g [00003310] le bot à fait 3,3 puis 1 donc doit venir à gauche des 3.
                    next_x, next_y = self.bot_last_hit[0] + self.bot_direction[0], self.bot_last_hit[1] + self.bot_direction[1]
                    if 0 <= next_x < 8 and 0 <= next_y < 8 and self.player_grid[next_x][next_y] not in [1, 3]: # Conditions d'existence du tir
                        tir = (next_x, next_y)
                    else:
                        # Si aucune direction valide, repasse en mode aléatoire
                        self.bot_direction = ()
                        tir = self.bot_targets.pop(0) if self.bot_targets else None # Continue si il reste des cible spécifique
            else:
                # Prend une cible parmi celles probables
                tir = self.bot_targets.pop(0) if self.bot_targets else None
        else:
            # Tir aléatoire
            while True:

                tir_x = random.randint(0, 7)
                tir_y = random.randint(0, 7)
                if self.player_grid[tir_x][tir_y] not in [1, 3]:  # Évite les cases déjà essayées
                    tir = (tir_x, tir_y)
                    break

        print('Bot turn ...')
        print(f'Cases adjacentes à vérifier : {self.bot_targets}')  # Debugging


        # Vérifie si un bateau est touché

        if tir is None:
        ################################################################################################################
            # C'est là pour décorer mais on garde quand même
            # raise TypeError('Tir is None : aucun tir valid trouvé') # J'espère ne pas avoir a y recourrir

            # Il y a un problème dans la logique que j'arrive pas a identifier donc on prie mtn

            # Dans la pratique, il est effectivement improbable que toutes les /cases adjacentes/ d'un bateau aient
            # été testées avant que le /bateau soit coulé/, sauf si un problème logique empêche le bot de correctement
            # "chasser" les cases adjacentes après avoir touché une partie du bateau.

            # Problèmes possible de l'erreur:
            # Fichier "code.py", ligne xxx, dans bot_turn
            # TypeError: l'objet 'NoneType' n'est pas itérable

            # Erreur dans la logique de génération des cases adjacentes
            # Erreur dans la logique de direction (self.bot_direction)
            # Erreur dans la logique de marquage des cases
            # Erreur dans la logique de vérification des bateaux coulés
            # Si le bot passe en mode aléatoire trop tôt, il pourrait manquer des cases adjacentes valides.

            # Désolé pour le pavé mais déja passé : 4h dessus
            # ChatGPT y est d'aucune aide potable

        ################################################################################################################

            print(f'Erreur: aucune cible valide trouvée. Le bot est cassé mais faut pas que ca se sache ;)')
            self.bot_targets = []
            self.bot_direction = ()
            self.bot_last_hit = False
            return

        x, y = tir
        if self.player_grid[x][y] == 2:  # 2 = bateau
            print(f'Bot à touché en {(x, y)}')
            self.player_grid[x][y] = 3  # Marque comme touché; 3 = bateau touché
            self.blink(x, y, ORANGE, ORANGE, blink_bots_play)  # Orange pour un tir qui touche

            # Le bot rejoue si il touche
            self.bot_attacked = False
            self.bot_attacking = True

            if not hasattr(self, "bot_direction") or not self.bot_direction:

        ########################################################################

            # hasattr check si un objet existe dans une class : hasattr(object, attribute_name)
            # Si il n'y a pas de direction, dans la class (hasattr)/ ou dans la fonction(self.bot_direction)
            # Détermine la direction si une deuxième case est touchée
            # (déjà dans un if statement qui dit que le bot viens de toucher)
            # Les tuples (0,1)(0,-1)(1,0)(-1,0) sont les offsets qu'on essaye pour "chasser" la bateau

        ########################################################################

                if self.bot_last_hit:
                    if x == self.bot_last_hit[0]:  # Même ligne que le tir précédent = direction verticale
                        self.bot_direction = (0, 1 if y > self.bot_last_hit[1] else -1) # (0,1) ou (0,-1) = verticale; selon si on monte ou descent (sur l'axe des ordonnées)
                    elif y == self.bot_last_hit[1]:  # Même colonne = direction horizontale
                        self.bot_direction = (1 if x > self.bot_last_hit[0] else -1, 0) # (1,0) ou (-1,0) = horizontale; selon si on va à droite ou à gauche (sur l'axe des abscisses)

            self.bot_last_hit = (x, y)  # Sauvegarde les  pour le round d'aprèscoordonnées du tir pour le round d'après

            # Vérifie si le bateau est coulé
            for ship in self.player_ships:
                if all(self.player_grid[sx][sy] == 3 for sx, sy in ship):  # Si toutes les cases du bateau sont touchées
                    if ship not in self.player_sunken_ships:
                        self.player_sunken_ships.append(ship)
                        for sx, sy in ship:
                            self.blink(sx, sy, RED, RED, blink_bots_play)  # Rouge pour un bateau coulé
                        self.bot_last_hit = None  # Réinitialise pour passer en mode aléatoire
                        self.bot_targets = []  # Vide les cibles adjacentes
                        self.bot_direction = None  # Réinitialise la direction

                    break


        else:
            self.player_grid[x][y] = 1  # Marque comme raté
            self.blink(x, y, GRAY, GRAY, blink_bots_play)  # Gris pour un tir raté
            print(f'Raté en {(x, y)}')

            # Le bot à raté c'est au tour du joueur
            self.bot_attacked = True
            self.bot_attacking = False

        # Affiche le plateau du joueur pour visualiser le tir
        self.display_grid(self.player_grid, is_player_turn=False)
        time.sleep(2)  # Ajoute un délai pour que le joueur puisse voir le (sinon ça pue)

        if self.current_player_sunken_ships != self.player_sunken_ships: # Si un nouveau navire est coulé alors la console rapelle tous les bateaux coulé (ca marche pas vraiment enfait)
            self.current_player_sunken_ships = self.player_sunken_ships
            print(f"Bateau coulé par le bot : {self.current_player_sunken_ships}")

        # Vérifie si le jeu est fini
        if all(tile != 2 for row in self.player_grid for tile in row):
            print("Le joueur a gagné !")
            self.game_running = False
            self.initialize_board("endGame_Lose") # Ici, "Lose" car c'est la fin du tour du bot
            return


        print('')
        # Fin du tour du bot

    def player_turn_logic(self):
        """
        Logique du joueur.

        Logique de la grid:
        0 = Rien
        1 = Tir raté
        2 = Bateau
        3 = Bateau touché

        Edit: Régler la répetition du "Bateau coulé par le joueur : {ship}" à chaque play

        """
        print("Player turn ...")
        joueur_a_joue = False
        tir_joueur = None  # Définit tir_joueur dans l'outer scope

        def handle_player_input(x, y, edge):
            """
            Callback pour gérer l'entrée du joueur via les boutons NeoTrellis.

            """
            nonlocal joueur_a_joue, tir_joueur # Global fonction mais local inner fonction.  Si questions, demander à Matteo :)
            if edge == NeoTrellis.EDGE_RISING and not joueur_a_joue:  # Si c'est le premier bouton touché
                tir_joueur = (x, y)
                joueur_a_joue = True

        # Configure les callbacks pour les inputs du joueur
        for y in range(8):
            for x in range(8):
                self.trellis.activate_key(x, y, NeoTrellis.EDGE_RISING)
                self.trellis.set_callback(x, y, handle_player_input)

        # Attend l'input du joueur
        while not joueur_a_joue:
            self.trellis.sync()
            time.sleep(0.01)


        # Gère le tir du joueur
        x, y = tir_joueur
        if self.bot_grid[x][y] == 2: # Bateau à l'endroit touché ?
            print(f'Joueur à touché en {(x,y)}')
            self.bot_grid[x][y] = 3  # Marque comme touché
            self.set_led(x, y, ORANGE)
            
            # Rejoue si touché
            self.bot_attacked = True
            self.bot_attacking = False

            # Vérifie si le bateau est coulé
            for ship in self.bot_ships:
                if all(self.bot_grid[x][y] == 3 for x, y in ship):  # Si toutes les cases du bateau sont touchées
                    if ship not in self.bot_sunken_ships: self.bot_sunken_ships.append(ship)
                    for x, y in ship:
                        self.set_led(x, y, RED)  # Rouge pour un bateau coulé
        elif self.bot_grid[x][y] == 0:
            print(f'Raté en {(x,y)}')
            self.bot_grid[x][y] = 1  # Marque comme raté
            self.set_led(x, y, GRAY)  # Gris pour un tir raté

            # Change de tour (raté = tour par tour)
            self.bot_attacked = False
            self.bot_attacking = True
        else:
            print("Déjà tiré ici (ouvre tes yeux enfait !)")


        # Fin du tour du joueur / Annonce serial
        if self.current_bot_sunken_ships != self.bot_sunken_ships: # Si un nouveau navire est coulé alors la console rapelle tous les bateaux coulé (ca marche pas vraiment enfait)
            self.current_bot_sunken_ships = self.bot_sunken_ships
            print(f"Bateau coulé par le joueur : {self.current_bot_sunken_ships}")

        # Vérifie si le jeu est fini
        if all(tile != 2 for row in self.bot_grid for tile in row):
            print("Le joueur a gagné !")
            self.game_running = False
            self.initialize_board("endGame_Win") # Ici, "Win" car c'est la fin du tour du joueur
            return

        print('')
        time.sleep(2)

    def main1(self):
        """
        Gestion du mode solo principal.

        Logique de la grid:
        0 = Rien
        1 = Tir raté
        2 = Bateau
        3 = Bateau touché

        """

        self.player_grid = [[0] * 8 for i in range(8)]  # Plateau du joueur
        self.bot_grid = [[0] * 8 for i in range(8)]  # Plateau du bot
        self.bot_last_hit = None
        self.bot_targets = []  # Cases autour d'un bateau touché (pour "tourné" autour)
        self.bot_attacking = True
        self.bot_attacked = False
        self.player_turn = False
        self.game_running = True
        self.bot_sunken_ships,self.current_bot_sunken_ships = [],[] # Debug purposes
        self.player_sunken_ships, self.current_player_sunken_ships = [],[] # Debug purposes

        ##################################################

        # Placement des bateaux par le joueur
        print("Placement des bateaux...")
        self.placement_bateaux()

        # --------------- Fast testing purposes -------------------
        #
        # Bateaux du joueur (hardcoded pour l'instant)
        # self.player_ships = [[(0, 4), (0, 5), (0, 6), (0, 7)],
        #                    [(5, 6), (6, 6), (7, 6)],
        #                   [(4, 3), (4, 4)]]
        #
        # ---------------------------------------------------------

        #Placement des bateaux du joueur sur la grille de jeu
        print('Bateaux du joueur :')
        for ship in self.player_ships:
            print(ship) # Affiche les coordonnées des bateaux du joueur (fraichement choisi)
            for x, y in ship:
                self.player_grid[x][y] = 2  # Bateaux


        ##################################################
        # Bateaux du bot (utilise placer_bateaux_bots)

        self.bot_ships = self.placer_bateaux_bots()
        print('Bateaux du bot :')
        for ship in self.bot_ships:
            print(ship) # Affiche les coordonnées des bateaux choisi par le bot
            for x, y in ship:
                self.bot_grid[x][y] = 2

        ##################################################


        while self.game_running:

            # Reset button ongoing dev (j'espère que personne ne lira ca et que j'aurais dev ca d'ici là)
            """
            # Vérifie si un reset a été demandé
            if self.reset_requested:
                print("Reset en cours...")
                self.reset_requested = False  # Réinitialise la demande de reset
                self.initialize_board("init")  # Réinitialise le plateau
                self.menu()  # Retourne au menu principal
                return  # Quitte la boucle principale

            """

            if self.bot_attacking:
                self.display_grid(self.player_grid, is_player_turn=False)  # Affiche le plateau du joueur
                self.bot_turn_logic()
            elif self.bot_attacked:
                self.display_grid(self.bot_grid, is_player_turn=True)  # Affiche le plateau du bot
                self.player_turn_logic()

        self.menu() # Sortie du while = fin de partie, retour au menu

    def kill_game(self):
        """
        Debugging purposes, kill game
        """
        self.game_running = False
        self.menu()
        return

#########################################################################################
############################ Mode 1v1 a partir de cette ligne ###########################
#########################################################################################


###########################################################################

    # La communication entre les plateaux et l'ordi/raspberri pi se fera a l'aide d'un protocole
    # de communication basé sur des messages simples.
    #
    # Exemple:
    #   Depuis le plateau (vers le script maître)
    #       PLACEMENT:x,y → un bouton a été appuyé                 (n'a pas été retenu)
    #       TIR:x,y → le joueur a tiré ici
    #       FIN → le joueur a fini
    #
    #   Depuis le maître (vers le plateau):                                            (aucun des exemples n'est utilisé mais vous avez compris le principe)
    #       LED:x,y,color → allumer une LED (color = green/red/blue)
    #       RESET → reset le plateau
    #       VICTOIRE → allumer toutes les LED en vert (par exemple)
    #       GAMEOVER → game over, les LED s'éteignent
    #       SCORE:x,y,valeur → afficher le score
    #
    #
    # Les fonctions suivante sont là pour decrypter les messages et les envoyés.
    # lire(plateau): plateau étant le port serial du plateau
    # envoyer(plateau,message): plateau étant le port serial du plateau et message le message à envoyer

###########################################################################


    def envoyer(self, message):
        """
        Essaye d'envoyer le message
        """
        try:
            communication.write((message + "\n").encode())
        except Exception as exept: # Génère un exeption pour le debug
            print("Erreur envoi:", exept)

    def lire(self):
        """
        Récupère les message
        """
        if communication.in_waiting:
            try:
                return communication.readline().decode().strip()
            except Exception as exept:
                print("Erreur lecture:", exept)
        return None

    def update_opponent_grid(self, x, y, result):
        """
        Met à jour la grille locale de l'adversaire en fonction du résultat du tir pour suivre la partie.
        x, y : Coordonnées du tir.
        result : Résultat du tir ("RATE", "TOUCHE", "COULE").

        Logique de la grid SPÉCIFIQUE à l'adversaire:
        0 = Rien
        1 = Tir raté
        2 = Bateau touché
        3 = Bateau coulé

        """
        if result == "RATE":
            self.opponent_grid[x][y] = 1  # Tir raté
        elif result == "TOUCHE":
            self.opponent_grid[x][y] = 2  # Bateau touché
        elif result == "COULE":
            #A faire la logique des bateaux coulés
            for ship in self.player_ships:
                if (x, y) in ship:
                    for cx, cy in ship:
                        self.opponent_grid[cx][cy] = 3  # Bateau coulé

    def display_opponent_grid(self):
        """
        Affiche l'état de la grille de l'adversaire sur les LEDs.
        """
        for y in range(8):
            for x in range(8):
                if self.opponent_grid[x][y] == 1:  # Tir raté
                    self.set_led(x, y, GRAY)
                elif self.opponent_grid[x][y] == 2:  # Bateau touché
                    self.set_led(x, y, ORANGE)
                elif self.opponent_grid[x][y] == 3:  # Bateau coulé
                    self.set_led(x, y, RED)

    def display_player_grid(self):
        """
        Affiche l'état de la grille du joueur sur les LEDs.
        """
        for y in range(8):
            for x in range(8):
                if self.player_grid[x][y] == 1:  # Tir raté
                    self.set_led(x, y, GRAY)
                
                elif self.player_grid[x][y] == 2:  # Bateau non touché par l'ennemis
                    # Bleu uniquement sur (player_grid)
                    for num_bateau, ship in enumerate(self.player_ships): # Enumerate pour récupérer l'index du bateau et mettre de la couleur
                        for gx, gy in ship:
                            self.set_led(gx, gy, couleurs_bateaux[num_bateau])  # Applique la couleur en fonction de l'index du bateau
                
                elif self.player_grid[x][y] == 3:  # Bateau touché
                    self.set_led(x, y, ORANGE)
                # elif self.player_grid[x][y] == 4: # Bateau coulé (dans la théorie ca marche mais au cas ou on le check manuellement en dessous)
                #     self.set_led(x, y, RED)
                else:
                    # Bateaux coulé
                    for ship in self.player_ships:
                        if all(self.player_grid[sx][sy] == 3 for sx, sy in ship):  # Si toutes les cases du bateau sont touchées
                                for sx, sy in ship:
                                    self.set_led(sx, sy, RED)

    def main2(self):
        """
        Mode 1v1

        Logique de la grid:
        0 = Rien
        1 = Tir raté
        2 = Bateau
        3 = Bateau touché
        4 = Bateau coulé

        """
        self.game_running = True
        self.player_ships = []
        self.player_grid = [ [0] * 8 for i in range(8)] # Grille joueur
        self.opponent_grid = [ [0] * 8 for i in range(8)]
        self.player_sunken_ships = []
        self.current_player_sunken_ships = []

        # Main loop
        while self.game_running:
            cmd = self.lire()
            if not cmd:
                continue
            if cmd == "DUO?":
                self.envoyer("YESDUO")
                print("En attente d'un adversaire...")
                continue

            # Placement demandé : retour READY
            if cmd == "PLACE":
                self.placement_bateaux()
                for ship in self.player_ships:
                    print(f'Bateau du joueur \n {ship}')
                    for x, y in ship:
                        self.player_grid[x][y] == 2
                self.envoyer("READY")

            # Demande de verification d'un tir : retour RESULT + [WIN,TOUCHE,RATE]
            elif cmd.startswith("TIR:"):
                _, coord = cmd.split(":")
                x, y = map(int, coord.split(","))
                if self.player_grid[x][y] == 2:  # Bateau touché
                    self.player_grid[x][y] = 3  # Marque comme touché
                    self.set_led(x, y, ORANGE)
                    for ship in self.player_ships:
                        if all(self.player_grid[sx][sy] == 3 for sx, sy in ship):  # Vérifie si le bateau est coulé
                            for sx, sy in ship:
                                self.player_grid[sx][sy] = 4  # Marque comme coulé
                                self.set_led(sx, sy, RED)
                            self.envoyer("RESULT:COULE")
                            break
                        else:
                            self.envoyer("RESULT:TOUCHE")
                else:
                    self.player_grid[x][y] = 1  # Marque comme raté
                    self.set_led(x, y, GRAY)
                    self.envoyer("RESULT:RATE")

            # Recupération des resultat du tir réalisé : retour None
            elif cmd.startswith("RESULT:"):
                result = cmd.split(":")[1]  # Extrait le résultat ("RATE", "TOUCHE", "COULE")
                x, y = self.last_shot  # Coordonnées du dernier tir
                self.update_opponent_grid(x, y, result)  # Met à jour la grille de l'adversaire
                self.display_opponent_grid()  # Met à jour l'affichage de la grille "Attauant"

            # Demande le tir du joueur : retour TIR:x,y
            elif cmd == "YOURTURN":
                print("C'est votre tour !")
                joueur_a_joue = False
                tir_joueur = None  # Définit tir_joueur dans l'outer scope

                def handle_player_input(x, y, edge):
                    """
                    Callback pour gérer l'entrée du joueur via les boutons NeoTrellis.

                    cf: player_turn_logic(self)

                    """
                    nonlocal joueur_a_joue, tir_joueur
                    if edge == NeoTrellis.EDGE_RISING and not joueur_a_joue:  # Si c'est le premier bouton touché
                        tir_joueur = (x, y)
                        joueur_a_joue = True

                # Configure les callbacks pour les inputs du joueur
                for y in range(8):
                    for x in range(8):
                        self.trellis.activate_key(x, y, NeoTrellis.EDGE_RISING)
                        self.trellis.set_callback(x, y, handle_player_input)

                # Attend l'input du joueur
                while not joueur_a_joue:
                    self.trellis.sync()
                    time.sleep(0.01)

                # Gère le tir du joueur
                x, y = tir_joueur
                self.last_shot = (x, y)  # Sauvegarde le tir pour traiter le résultat plus tard
                print(f"Tir envoyé en ({x}, {y})")
                self.envoyer(f"TIR:{x},{y}")  # Envoie le tir à l'adversaire

#########################################################################################
############################ Kube Kube à partir de cette ligne ##########################
#########################################################################################

###########################################################################

    # Le jeu ne marche pas bien et c'est pas possible d'en sortir sans débrancher - rebrancher
    # autrement dit c'est pété, et claqué au sol. 
    #
    # C'était plus une sidequest, 
    # néanmoins ca a le mérite d'exister
    # pout activer le jeu il faut appuyer en bas à droite en coordonnées (7,7) (si on se place sur du 8,8). hf

###########################################################################


    def start_kube(self):
        """
        Initialise le jeu Kube Kube (c'est complétement du plagiat).
        Une fonction qui appelle une fonction c'est juste pour le style du menu :)
        Pour sortir du jeu, faire 3 fautes sur la même case. ( en dev )
        """

        self.kube_generate_grid()

    def kube_generate_grid(self, kube_level = 1):
        """
        Génère la grid avec une couleur de base et une seule case légèrement différenteq qu'il faut cliquer.
        Retour au menu si loose ou si 3 fois la même erreur au même endroit. (tu peux en théorie pas perdre car pas de time limit)
        """

        while True:

            kubegame_active = True
            error_count = {} # Compteur d'erreurs pour chaque case (coord) (x,y) : [erreur, niveau]

            kube_base_color = (
                    random.randint(50, 200),
                    random.randint(50, 200),          # Couleur que prendra la grid pour le premier tour
                    random.randint(50, 200),
            ) 

            # Calculer un delta de couleur selon le niveau, pour être de plus en plus proche de la couleur de base
            difference = max(5, 60 - kube_level * 3) # Le changement de teinte est toujours de la même diff
            # En dessous de 5 c'est juste impossible

            # Générer une couleur légèrement différente pour la case à trouver
            # La différence s'applique sur les 3 composantes Rouge Vert et Bleu
            # Le min(255,...) évite de dépasser si la diff est trop importante
            # le max(0,...) évite de sortir si la diff est trop basse
            dr = max(0, min(255, kube_base_color[0] + random.choice([-difference, difference])))
            dg = max(0, min(255, kube_base_color[1] + random.choice([-difference, difference])))
            db = max(0, min(255, kube_base_color[2] + random.choice([-difference, difference])))

            kube_target_color = (dr,dg,db)

            # Choisit une position aléatoire pour la case cible
            target_x = random.randint(0, 7)
            target_y = random.randint(0, 7)
            kube_target = (target_x, target_y)


            def kube_handle_click(x, y, edge):
                """
                Réagit à un clic pendant le jeu Kube Kube.
                """
                nonlocal kube_level, kubegame_active

                if edge == NeoTrellis.EDGE_RISING:
                    if (x, y) == kube_target:
                        print("Kube found")
                        time.sleep(0.3)
                        kube_level += 1  # Augmente le niveau
                        kubegame_active = False  # Arrête la boucle active pour générer une nouvelle grille
                    else:
                        print("Mauvais kube !")
                        # Incrémente le compteur d'erreurs pour cette case (chaque case à son compteur)
                        if (x, y) not in error_count: # N'as pas été cliqué précédement ?
                            error_count[(x, y)] = [0, kube_level]
                        else:
                            if error_count[(x, y)] [1] == kube_level: # Est ce une erreur répeter sur le même niveau ?
                                error_count[(x, y)] [0] += 1 # Si oui : ajoute un erreur au compte
                            else:
                                error_count[(x, y)] = [1, kube_level] # Si non : remet l'erreur à 1 et update le niveau

                        # Vérifie si 3 erreurs ont été faites sur la même case
                        if error_count[(x, y)] [0] >= 3:
                            print("3 erreurs sur la même case. Fin du jeu.")
                            kubegame_active = False
                            self.menu()  # Retourne au menu
                            return


            # Affichage de la grille
            for y in range(8):
                for x in range(8):
                    self.trellis.activate_key(x, y, NeoTrellis.EDGE_RISING)
                    self.trellis.set_callback(x, y, kube_handle_click)

                    # Définit la couleur de la grille
                    if (x, y) == kube_target:
                        self.set_led(x, y, kube_target_color)  # Case cible
                        print(f"Case cible : {kube_target} en {kube_target_color} sur du {kube_base_color}")
                    else:
                        self.set_led(x, y, kube_base_color)  # Cases normales
            
            while kubegame_active:
                self.trellis.sync()
                time.sleep(0.01)
            
            # Si le jeu est terminé (kubegame_active est False), on recommence avec le niveau suivant
            if not kubegame_active and kube_level > 0:
                continue



# Détection au démarrage
waiting_animation()
mode = detect_mode()

if mode == "1v1":
    print("Communication usb_cdc.data ouverte\n")
else:
    print("Mode PVE activé (aucune connexion USB / bus_usb_cdc check boot.py)\n")


# Création et initialisation du gestionnaire
manager = TrellisManager(trellis)
manager.initialize_board("init")
manager.menu()



# Boucle principale
while True:
    """
    Boucle principale du plateau. Pricipalement pour le menu et l'init.

    Le debug qui se trouvait ici est maintenant dans menu()

    """

    trellis.sync()  # Met à jour les événements des boutons
    time.sleep(0.005)
