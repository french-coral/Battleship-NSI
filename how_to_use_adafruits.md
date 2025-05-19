# 🛠️ Utilisation des cartes Feather M4 avec un NeoTrellis 8x8 (Adafruit)

---

## 📦 Matériel utilisé

- **Carte principale** :
    
    ➔ **Adafruit Feather M4 Express** — Un microcontrôleur rapide et flexible, compatible **CircuitPython**.
    
- **Grille LED + boutons** :
    
    ➔ **Adafruit NeoTrellis 8x8** —
    
    Une grille **8x8 de boutons** sensibles au toucher, chacun avec une **LED RGB programmable**.
    

---

## ⚡ Connexion entre Feather et NeoTrellis

La NeoTrellis se connecte **par bus I2C** (communication série simple) :

| Feather Pin | NeoTrellis |
| --- | --- |
| 3V | VIN |
| GND | GND |
| SCL (I2C Clock) | SCL |
| SDA (I2C Data) | SDA |

➔ **4 fils** suffisent pour que la Feather parle à la NeoTrellis.

**Important** :

- La NeoTrellis doit être alimentée en **3.3V** (ce que fournit la Feather).
- Les données I2C passent en **SDA/SCL standards** (CircuitPython gère ça automatiquement).

Ca en théorie vous n’avez pas à gérer sauf si vous êtes des baltrous qui ont pété un cable ou une soudure. Force à vous ;)

---

## 🧠 Comment ça fonctionne côté logiciel

- La **Feather** lit en permanence l'état des 64 touches (8x8) grâce au bus I2C.
- Chaque **LED** derrière un bouton peut être allumée **individuellement** et **en couleur**.
- Il est possible de :
    - **Activer une LED** quand on appuie sur un bouton,
    - **Changer la couleur** d'une case pour indiquer un état (par ex. tir raté, touché, coulé),
    - **Désactiver** toutes les LEDs pour réinitialiser la grille.

**CircuitPython** + la bibliothèque **Adafruit NeoTrellis** rendent tout ça **très simple**.

Architecture de code que tu peux récup :

```python
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
RED = (255, 0, 0)
GREEN = (0,255,0)
BLUE = (0, 0, 255)

#Le reste des fonctions utiles se trouveront dans le code.py du github (@french-coral)
```

---

## 📚 Ce qu’un futur utilisateur doit savoir

| Sujet | Détail |
| --- | --- |
| **Alimentation** | La Feather alimente le Trellis via 3V/GND. Ou juste l’USB. |
| **Communication** | Les données passent par I2C (2 broches : SDA/SCL). Enfait y’a un port .console qui gère la console serial et un .data qui est la communication par port USB. |
| **Programmation** | Utiliser CircuitPython et la librairie `adafruit_neotrellis`. |
| **Touch detection** | Chaque bouton est détectable par événement (appui court, appui long possible). |
| **RGB LEDs** | Les LEDs peuvent afficher toutes les couleurs en RGB 24-bit. |
| **Facilité** | Très simple pour créer des jeux, des interfaces interactives, des panneaux lumineux. |
