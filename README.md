SI TU CHERCHE UNE BASE POUR UTILISER LES PLATEAUX C'EST DANS LE "how_to_use_adafruits.md".
Bonne chance -Le mec qu'était là avant.


### Environnement requis

- **Python version** : Python 3.11 recommandé
- **Bibliothèque obligatoire** :
    - requirement.txt
    - `pyserial` → installer via :
        
        ```bash
        pip install pyserial
        ```
        
- **Système recommandé** : Raspberry Pi OS 64bit full (ou PC Linux récent)

### Matériel nécessaire

- 2 x Feather M4 Express (Adafruit) (Plateaux leds 8 x 8)
- 2 x Câbles MicroUSB pour Feather
- 1 x Chargeur USB-C (pour Raspberry Pi 4)
- 1 x MicroHDMI → HDMI (si utilisation d'écran)
- 1 x Câble Ethernet (ou Wi-Fi configuré) pour SSH
- **Conseillé** : Hub USB alimenté (si problèmes de reset USB)

Le projet s’est arrêté ici, donc on a pas fait la Raspberry au final. Mais l’architecture a été faite.

### Outils de développement

- **MU Editor** (très simple pour CircuitPython) : https://codewith.mu/

ou

- **Visual Studio Code** avec extensions :
    - "CircuitPython" officielle Adafruit
    - "Serial Monitor" intégré



## Architecture du projet

```markdown
┌────────────────────────┐         USB Serial        ┌─────────────────────────┐
│ Raspberry Pi / PC      │ ◄────────────────────────►│ Feather M4 (Plateau 1)  │
│ (main.py tourne ici)   │                           └─────────────────────────┘
│                        │                            ┌─────────────────────────┐
│                        │ ◄────────────────────────► │ Feather M4 (Plateau 2)  │
└────────────────────────┘         USB Serial         └─────────────────────────┘
                                        
```



## Fonctionnement

- **main.py** :
    - Gère les connexions USB
    - Lance les phases de placement (`PLACE`) et de jeu (`YOURTURN`, `TIR:x,y`)
    - Synchronise l'état du jeu entre les plateaux
- **code.py** (sur chaque Feather) :
    - Place les bateaux
    - Envoie les coordonnées de tirs
    - Met à jour l'affichage LED selon les événements reçus

Plus chaque Feather à un mode solo.



## Déroulement d'une partie

1. `main.py` détecte 2 Feather connectées.
2. Il envoie `PLACE` → Les joueurs placent leurs bateaux sur leur grille.
3. Les Feather envoient leurs positions (`BOATS:`) au serveur.
4. Le serveur échange les données et lance la partie.
5. À chaque tour :
    - Envoi de `YOURTURN`
    - Réponse `TIR:x,y`
    - Résolution locale sur chaque Feather (affichage Orange/Rouge/Gris)

Fin quand un joueur a coulé tous les bateaux adverses (`RESULT:WIN`).



## Exemple de service `systemd` pour autostart (raspberry pi)

Pour lancer automatiquement `main.py` au démarrage :

**1. Créer le service**

```bash
sudo nano /etc/systemd/system/feather.service
```

**2. Contenu du fichier :**

```idris
[Unit]
Description=Autostart du main.py DuoBattleship
After=network.target

[Service]
ExecStart=/usr/bin/python3 /home/pi/project/main.py
WorkingDirectory=/home/pi/project/
Restart=always
RestartSec=5
StandardOutput=file:/home/pi/project/logs/feather.log
StandardError=file:/home/pi/project/logs/feather_error.log
User=pi

[Install]
WantedBy=multi-user.target

```

**3. Commandes pour activer :**

```bash
sudo systemctl daemon-reload
sudo systemctl enable feather.service
sudo systemctl start feather.service
sudo systemctl status feather.service
```



## Conseils pratiques

- **Utiliser un hub USB alimenté** pour éviter les resets USB si possible.
- **Brancher les Feather AVANT de lancer `main.py`** si pas de Hub.
- **Toujours vérifier que `pyserial` est bien installé**.



## Futures améliorations possibles

- Communication Feather ↔ Feather directe via **UART** (2 fils) pour éviter l'USB.
- Passage à **BLE** (Bluetooth Low Energy) pour un mode sans fil propre. (besoin de commandé un module)

Pour configurer un environnement virtuel (`venv`) dans Visual Studio Code (VSCode) pour un projet utilisant un **Feather M4** (ou tout autre microcontrôleur), tu peux suivre ces étapes. Assurons-nous que tu as installé les outils nécessaires pour travailler avec la Feather M4 (qui utilise généralement des bibliothèques Python comme `Adafruit_CircuitPython_Board` ou `Adafruit_CircuitPython_FeatherM4`).

### Étape 1 : Installer les prérequis

1. **Installer Python** : Assure-toi d'avoir Python installé sur ton système. Tu peux le télécharger ici : [python.org](https://www.python.org/downloads/).
2. **Installer VSCode** : Si ce n'est pas déjà fait, télécharge et installe Visual Studio Code depuis [Visual Studio Code](https://code.visualstudio.com/).

### Étape 2 : Créer un projet dans VSCode

1. Ouvre VSCode et crée un nouveau dossier pour ton projet.
2. Ouvre ce dossier dans VSCode (`File > Open Folder...`).

### Étape 3 : Créer un environnement virtuel (venv)

1. Ouvre le terminal intégré de VSCode : `Terminal > New Terminal` ou utilise le raccourci `Ctrl + ~`.
2. Dans le terminal, crée un nouvel environnement virtuel avec la commande suivante :
    - Sous Windows :
        
        ```
        py -m venv nom_du_env
        ```
        
3. Remplace `nom_du_env` par le nom que tu souhaites donner à ton environnement virtuel (par exemple `feather_m4_venv`).

### Étape 4 : Activer l'environnement virtuel

- Sous **Windows**, utilise la commande :
    
    ```
    .\nom_du_env\Scripts\activate
    ```
    

Lorsque l'environnement virtuel est activé, tu devrais voir quelque chose comme ceci dans ton terminal : `(nom_du_env)` devant le prompt.

### Étape 5 : Installer les bibliothèques nécessaires

1. Avec l'environnement virtuel activé, tu peux maintenant installer les bibliothèques nécessaires pour ton projet, comme celles d'Adafruit pour la Feather M4. Par exemple :
    
    ```
    pip install adafruit-circuitpython-busdevice
    ```
    
2. Si tu prévois d'utiliser d'autres bibliothèques Python spécifiques au Feather M4, installe-les de la même manière.

### Étape 6 : Configurer VSCode pour utiliser l'environnement virtuel

1. Ouvre le fichier de ton projet dans VSCode.
2. Clique sur le sélecteur de l'interpréteur Python dans le coin inférieur gauche de VSCode, ou utilise le raccourci `Ctrl + Shift + P` et tape `Python: Select Interpreter`.
3. Sélectionne l'interpréteur Python de ton environnement virtuel (il devrait apparaître sous la forme `./nom_du_env/bin/python` sur macOS/Linux ou `.\nom_du_env\Scripts\python.exe` sous Windows).

### Étape 7 : Développer et téléverser sur la Feather M4

1. Si tu veux téléverser du code sur ton Feather M4, tu devras utiliser un outil comme **CircuitPython** (ou un autre système d'exploitation compatible avec ton microcontrôleur).
2. Si tu utilises CircuitPython, assure-toi que le périphérique est bien détecté par ton ordinateur et utilise un éditeur de code comme `Mu` ou un terminal pour envoyer le code au microcontrôleur.

### Étape 8 : Créer un fichier `requirements.txt` (optionnel)

Si tu veux partager ou reproduire ton environnement facilement, tu peux créer un fichier `requirements.txt` pour ton projet :

1. Dans le terminal, exécute :
    
    ```
    pip freeze > requirements.txt
    ```
    

Cela générera un fichier `requirements.txt` avec toutes les bibliothèques installées dans ton environnement virtuel.

```jsx
pip install -r requirements.txt
```
