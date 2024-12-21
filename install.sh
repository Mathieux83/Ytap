#!/bin/bash

# filepath: ytpd/install.sh

# Installer les dépendances système
sudo apt update
sudo apt install -y fzf mpv yt-dlp python3 python3-pip python3-venv

# Créer et activer un environnement virtuel
python3 -m venv venv
source venv/bin/activate

# Installer les dépendances Python
pip install -r requirements.txt

# Message de confirmation
echo "Installation terminée. Pour démarrer l'application, exécutez 'source venv/bin/activate' puis 'python3 ytap.py'."