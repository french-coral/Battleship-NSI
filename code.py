"""
########################################################
########################################################

Les commentaires présents le long de ce code ont été corrigé, verifié et clarifié, il se peut que certains "franglais"
s'y glisse, je m'en excuse.
J'espère être le plus claire possible. Bonne chance.
En cas de question spécifique et TRES technique demandé à : Noah

########################################################
########################################################

Informations sur le code / jeu :
- Le jeu est un jeu de 2 joueurs (Bataille Navale).
- Le plateau est un 8x8.
- Tour par tour.

- Chaque joueur a une flotte de 3 navires : Grand => 4 cases / Moyen => 3 cases /Petit => 2 cases
- Le joueur doit choisir la position de ses navires sur le plateau.  // En developpement
- Le joueur peut choisir la position des navires (manuel, automatique) // En developpement (on peut espérer)
- Le bot a ses navires positionnés automatiquement sur le plateau.

- Menu avec "Solo" et "Duo" mode.  // vouer à changer
- Un mode solo est disponible, il est codé sur le plateau directement.

- Le mode duo est disponible seulement si les 2 plateaux sont branchés.

########################################################
########################################################

"""

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
GREEN = (0,255,0)
FIN_COLOR = None # Pour les animation de fin de solo mode
MAGENTA = (255, 0, 255)
RED = (255, 0, 0)
GRAY = (100, 100, 100)  # Gris pour les tirs ratés du bot
ORANGE = (255, 165, 0)  # Orange pour les tirs qui touchent un bateau

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

        Le but est l'animation du board qui ce clear donc la couleur dépend du "couleur_gradient",
        plus il est élevé plus la différence des couleurs du dégradé seront marquées.

        Animations (step):
        - "Menu" = blue / light blue
        - "endGame" = Green victory animation + multipastel colors clear animation
        - "init" = Initialisation du plateau

        """
        if step == "menu":
            couleur_gradient = 5
        elif step == "endGame_Win" or step == "endGame_Lose":
            couleur_gradient = 150
        else: #Current else : "init"
            couleur_gradient = 32


        if couleur_gradient == 150 :# End animation
            if step == "endGame_Win": FIN_COLOR = GREEN
            else: FIN_COLOR = RED
            for r in range(3):
                for i in range(8):
                    for j in range(8):
                        self.set_led(i, j, FIN_COLOR)
                for i in range(8):
                    for j in range(8):
                        self.set_led(i, j, OFF)


        for y in range(8):
            for x in range(8):
                self.trellis.activate_key(x, y, NeoTrellis.EDGE_RISING)
                self.trellis.set_callback(x, y, self.handle_button_test) # associe la fonction handle quand le (x,y) est cliqué. ps: si question sur le callback demander à Matteo ;)

                # Applique un dégradé
                gradient_color = (x * couleur_gradient, y * couleur_gradient, 150)
                self.set_led(x, y, gradient_color)
                time.sleep(0.02)


        # Configure le bouton de reset (ne marche visiblement pas donc on va le comment out temporairement)
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

        Edit: Ne marche absolument pas, besoin d'une alternative.  04/04

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


    def handle_menu(self, x, y, edge):
        """
        Gère le choix du menu en fonction du bouton pressé

        Edit: Sera modifier si déplacer sur raspberry pi.  03/04
        """
        if edge == NeoTrellis.EDGE_RISING:
            if (x, y) in [(1,1), (1,2)]:  # Si on appuie sur la partie "Solo"
                self.menu_type = 'Solo'
                self.initialize_board("menu")
                # self.initialize_board("endGame_Lose") #/Debug/ Animation testing purposes
                self.main()


            elif (x, y) in [(5,1), (5,2), (6,1), (6,2)]:  # Si on appuie sur "Duo"
                self.menu_type = 'Duo'

            print(f"Mode sélectionné : {self.menu_type}")


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
                    bateau_en_cours.remove((x, y))
                    self.set_led(x, y, OFF)  # Éteint la LED
                    if len(bateau_en_cours) == 0:
                        direction = None  # Réinitialise la direction si aucune case n'est sélectionnée
                    return

                # Si aucune case n'a encore été sélectionnée pour ce bateau
                if not bateau_en_cours:
                    bateau_en_cours.append((x, y))
                    self.set_led(x, y, GREEN)  # Marque la première case en vert
                elif len(bateau_en_cours) == 1: # Une seule case posée
                    # Détermine la direction à partir de la deuxième case
                    if abs(x - bateau_en_cours[0][0]) == 1 and y == bateau_en_cours[0][1]: # Vérifie si les cases sont adjacentes + sur l'axe des abscisse ('y' ne change pas)
                        direction = "Horz"  # Horizontal
                    elif abs(y - bateau_en_cours[0][1]) == 1 and x == bateau_en_cours[0][0]: # Vérifie si les cases sont adjacentes + sur l'axe des ordonnées ('x' ne change pas)
                        direction = "Vert"  # Vertical
                    else:
                        print("Case invalide pour la direction.")
                        return

                    bateau_en_cours.append((x, y))
                    self.set_led(x, y, GREEN)  # Marque la deuxième case en vert


                else: # Pour le placement du bateau 3 et 4; equivalent d'un: elif len(bateau_en_cours) == 3 or 4.

                    # Ajoute les cases suivantes dans la direction déterminée
                    if direction == "Horz": # Devant ou derrière la selection déjà faite Horizontalement
                        if x == bateau_en_cours[-1][0] + 1 and y == bateau_en_cours[-1][1]: # Derrière Horizontalement
                            bateau_en_cours.append((x, y))
                            self.set_led(x, y, GREEN)
                        elif x == bateau_en_cours[0][0] - 1 and y == bateau_en_cours[0][1]: # Devant Horizontalement
                            bateau_en_cours.insert(0, (x, y))
                            self.set_led(x, y, GREEN)
                        else:
                            print("Case invalide pour continuer le bateau. C'est pas horizontale")
                            return
                    elif direction == "Vert": # Devant ou derrière la selection déjà faite Verticalement
                        if y == bateau_en_cours[-1][1] + 1 and x == bateau_en_cours[-1][0]: # Derrière Verticalement
                            bateau_en_cours.append((x, y))
                            self.set_led(x, y, GREEN)
                        elif y == bateau_en_cours[0][1] - 1 and x == bateau_en_cours[0][0]: # Devant Verticalement
                            bateau_en_cours.insert(0, (x, y))
                            self.set_led(x, y, GREEN)
                        else:
                            print("Case invalide pour continuer le bateau. C'est pas verticale")
                            return

                # Vérifie si le bateau est complètement placé
                if len(bateau_en_cours) == tailles_bateaux[bateau_actuel]:
                    # Marque le bateau comme placé (bleu)
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
                        self.trellis.clear_callbacks()  # Désactive les callbacks
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


    def menu(self):
        """
            Set les leds et bouttons du menu en fonction du  type de menu
            solo: I
            duo: I et II (sur le menu)

            Edit : Vouer à être modifier avec le mode duo gérer sur raspberry.  03/04
        """
        leds_ = [(1,1),(1,2),(5,1),(5,2),(6,1),(6,2)]  # Boutons du menu
        if mode == 'PVE':
            for i in range(2):
                self.set_led(leds_[i][0],leds_[i][1], BLUE)
                self.trellis.activate_key(leds_[i][0], leds_[i][1], NeoTrellis.EDGE_RISING)
                self.trellis.set_callback(leds_[i][0], leds_[i][1], self.handle_menu)
            for n in range(2,6):
                self.set_led(leds_[n][0],leds_[n][1], RED) #Mode de jeu pas dispo donc rouge
        else:
            for i in range(6):
                self.set_led(leds_[i][0],leds_[i][1], BLUE)
                self.trellis.activate_key(leds_[i][0], leds_[i][1], NeoTrellis.EDGE_RISING)
                self.trellis.set_callback(leds_[i][0], leds_[i][1], self.handle_menu)

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
                        self.set_led(x, y, BLUE)  # Bleu pour un bateau non touché (uniquement pour player_grid)
                elif grid[x][y] == 1:  # Tir raté
                    self.set_led(x, y, GRAY)  # Gris pour un tir raté
                else:  # Case vide
                    self.set_led(x, y, OFF)

    def bot_turn(self):
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
                        self.bot_direction = None
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

        # Vérifie si un bateau est touché
        x, y = tir
        if self.player_grid[x][y] == 2:  # 2 = bateau
            print(f'Bot à touché en {(x, y)}')
            self.player_grid[x][y] = 3  # Marque comme touché; 3 = bateau touché
            self.set_led(x, y, ORANGE)  # Orange pour un tir qui touche

            if not hasattr(self, "bot_direction") or not self.bot_direction: # Si il n'y a pas de direction, dans la class (hasattr) ou dans la fonction(self.bot_direction)
                #
                # Détermine la direction si une deuxième case est touchée
                # (déjà dans un if statement qui dit que le bot viens de toucher)
                # Les tuples (0,1)(0,-1)(1,0)(-1,0) sont les offsets qu'on essaye pour "chasser" la bateau
                #
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
                        print(f"Bateau coulé par le bot : {ship}") # // A FIX => si 2 bateaux coulé = 2 print (c'est pas ce qu'on veut)
                        for sx, sy in ship:
                            self.set_led(sx, sy, RED)  # Rouge pour un bateau coulé
                        self.bot_last_hit = None  # Réinitialise pour passer en mode aléatoire
                        self.bot_targets = []  # Vide les cibles adjacentes
                        self.bot_direction = None  # Réinitialise la direction

                    break


        else:
            self.player_grid[x][y] = 1  # Marque comme raté
            self.set_led(x, y, GRAY)  # Gris pour un tir raté
            print(f'Raté en {(x, y)}')

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
        self.bot_attacking = False
        self.bot_attacked = True

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

        # print(f"Joueur a tiré en {tir_joueur}") #/Debug/ Ca spam un peu trop la console

        # Gère le tir du joueur
        x, y = tir_joueur
        if self.bot_grid[x][y] == 2: # Bateau à l'endroit touché ?
            print(f'Joueur à touché en {(x,y)}')
            self.bot_grid[x][y] = 3  # Marque comme touché
            self.set_led(x, y, ORANGE)

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
        self.bot_attacked = False
        self.bot_attacking = True

    def main(self):
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

        # Bateaux du joueur (hardcoded pour l'instant)
        # self.player_ships = [[(0, 4), (0, 5), (0, 6), (0, 7)],
        #                    [(5, 6), (6, 6), (7, 6)],
        #                   [(4, 3), (4, 4)]]

        for ship in self.player_ships:
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

            # Reset button ongoing dev
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
                self.bot_turn()
            elif self.bot_attacked:
                self.display_grid(self.bot_grid, is_player_turn=True)  # Affiche le plateau du bot
                self.player_turn_logic()

        self.menu() # Sortie du while = fin de partie, retour au menu


# Création et initialisation du gestionnaire
manager = TrellisManager(trellis)
manager.initialize_board("init")
manager.menu()

#manager.benchmark(0,1)

# Boucle principale
while True:
    trellis.sync()  # Met à jour les événements des boutons
    time.sleep(0.005)

