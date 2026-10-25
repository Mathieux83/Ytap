# Ytap

Ytap is a cross-platform terminal application for searching YouTube and playing
audio with mpv or VLC. It supports Linux and Windows. `fzf` is optional; without
it, Ytap uses numbered menus.

## Prerequisites

### Linux

Install Python 3.10 or newer, pipx, Git, and either mpv or VLC using your
distribution's package manager. For example:

```bash
# Arch Linux
sudo pacman -S python python-pipx git mpv

# Debian / Ubuntu
sudo apt install python3 python3-pipx git mpv

# Fedora
sudo dnf install python3-pipx git mpv
```

VLC can be installed instead of mpv. Install `fzf` if you want its interactive
selection interface; it is not required.

### Windows

Install Python 3.10 or newer, Git, and pipx. Install either mpv or VLC separately.
Make sure the player's executable is on `PATH`. For VLC installed in a
non-standard location, set `YTAP_VLC_PATH` to the executable path.

## Install

After installing the prerequisites, the Ytap installation command is the same
on Linux and Windows:

```console
pipx install git+https://github.com/Mathieux83/Ytap.git
```

The Git URL installation requires Git. Once installed, pipx makes `ytap`
available as a terminal command. If the command is not found after installing
pipx, run `pipx ensurepath` and restart the terminal.

## First use

Ytap uses a YouTube Data API v3 key. Create a key in the Google Cloud Console,
then save it through the interactive prompt:

```console
ytap configure
ytap
```

The key is stored in the operating system's user configuration directory using
`platformdirs` (XDG configuration directory on Linux, the appropriate per-user
configuration directory on Windows). Alternatively, set `YTAP_API_KEY` in the
environment; this takes precedence over the saved key.

## Update and uninstall

```console
pipx upgrade ytap
pipx uninstall ytap
```

## Development

Install from a clone in editable mode and run the test suite:

```console
python -m venv .venv
# Linux:
source .venv/bin/activate
# Windows PowerShell:
# .venv\Scripts\Activate.ps1
python -m pip install -e .
python -m unittest discover -s tests -v
```

On other Linux distributions, install Python, pip, Git, and mpv or VLC using the
distribution's package manager, then use a virtual environment as above. Ytap's
Python package does not install the external audio player.

The automated tests cover packaging commands, configuration, simulated YouTube
API responses, and missing optional programs on Linux and Windows. Audio playback
itself should also be checked manually with the chosen player.
