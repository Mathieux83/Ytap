#!/bin/sh
set -eu

# Debian/Ubuntu helper; other systems should follow the README prerequisites.
sudo apt-get update
sudo apt-get install -y git pipx mpv
pipx ensurepath
pipx install git+https://github.com/Mathieux83/Ytap.git

printf "%s\n" "Ytap installed. Restart your terminal if the 'ytap' command is not on PATH."