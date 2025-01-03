# YouTube Audio Player aka ytap

## Installation des dépendances

### Pour Ubuntu/Debian
Vous pouvez installer les dépendances avec les commandes suivantes :
```bash
sudo apt install fzf mpv yt-dlp
```
Pour les autres distributions linux et MacOS
Vous pouvez installer les dépendances avec les commandes suivantes :
```bash
python3 -m pip install -r requirements.txt
brew install fzf mpv yt-dlp
```
si python3 n'est pas installé, vous pouvez l'installer avec la commande suivante :
```bash
sudo apt install python3
```
si pip n'est pas installé, vous pouvez l'installer avec la commande suivante :
```bash
sudo apt install python3-pip
```
ou
```bash
sudo python3 -m pip install --upgrade pip
```
Installation des dépendances avec pip
```bash
pip install -r requirements.txt
```
Si pip ne fonctionne pas, vous pouvez essayer avec pip3
```bash
pip3 install -r requirements.txt
```
Si pip3 ou pip ne fonctionne pas, vous pouvez essayer avec venv
```bash
python3 -m venv venv
source venv/bin/activate
pip3 install -r requirements.txt
```
### Pour Windows 
Vous pouvez installer les dépendances avec les commandes suivantes :
```bash
python -m pip install -r requirements.txt
choco install fzf mpv yt-dlp
```
Si python n'est pas installé, vous pouvez l'installer avec la commande suivante :
```bash
choco install python
```
si pip n'est pas installé, vous pouvez l'installer avec la commande suivante :
```bash
choco install pip
```
Si pip ne fonctionne pas, vous pouvez essayer avec venv
```bash
python -m venv venv
venv\Scripts\activate
python -m pip install -r requirements.txt
```
### Configuration

Importez votre clé API YouTube dans le fichier `API_KEY` pour pouvoir utiliser les fonctionnalités de recherche et de lecture de vidéos YouTube.

#### Installation

```bash
chmod +x install.sh
```
Après l'installation, vous pouvez activer l'environnement virtuel et exécuter le script avec la commande suivante :
```bash
source venv/bin/activate
python3 ytap.py
```

##### Utilisation

```bash
python3 ytap.py
``` 
##### Utilisation classique des raccourcis clavier pour naviguer dans les résultats de recherche et lire les vidéos avec mpv et fzf.

* flèches haut et bas pour naviguer dans les résultats de recherche
* enter pour lire la vidéo sélectionnée
* ESC pour quitter le programme / retour menu principal
