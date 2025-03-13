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
    pip install adafruit-circuitpython-featherm4 (Potentiel rattage)
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
