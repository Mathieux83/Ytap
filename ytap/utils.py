import requests
import subprocess
import sys
import os
import yt_dlp
from pathlib import Path
import time
import json

# Définir le chemin du fichier API_KEY en fonction du répertoire du projet
BASE_DIR = Path(__file__).resolve().parent
API_KEY_FILE_PATH = BASE_DIR / 'API_KEY'

# Lire la clé API depuis le fichier config/API_KEY
try:
    with open(API_KEY_FILE_PATH, 'r') as file:
        API_KEY = file.read().strip()
except FileNotFoundError:
    print("[red]API_KEY file not found. Please create an API_KEY file with your YouTube API key.")
    sys.exit(1)
except Exception as e:
    print(f"[red]An error occurred while reading the API_KEY file: {e}")
    sys.exit(1)

# Vérifier si fzf est installé
try:
    subprocess.run(['fzf', '--version'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)
    fzf = True
except FileNotFoundError:
    fzf = False
    ## print("[yellow]fzf n'est pas installé, une version classique du terminal sera utilisée.")

SEARCH_URL = 'https://www.googleapis.com/youtube/v3/search'
VIDEO_URL = 'https://www.youtube.com/watch?v='
PLAYLIST_URL = 'https://www.googleapis.com/youtube/v3/playlistItems'

def search_youtube(query, search_type='video', event_type=None):
    params = {
        'part': 'snippet',
        'q': query,
        'key': API_KEY,
        'maxResults': 20,
        'type': search_type
    }
    if event_type:
        params['eventType'] = event_type
    
    try:
        response = requests.get(SEARCH_URL, params=params)
        response.raise_for_status()  # Raise exception for 4XX/5XX responses
        data = response.json()

        if 'items' in data and len(data['items']) > 0:
            results = []
            for item in data['items']:
                # Vérifier si 'playlistId' est présent dans l'élément
                if search_type == 'playlist' and 'playlistId' in item['id']:
                    results.append((item['id']['playlistId'], item['snippet']['title']))
                elif search_type != 'playlist':
                    # Pour les vidéos ou autres types, on les ajoute avec leur ID spécifique
                    results.append((item['id'].get(f'{search_type}Id'), item['snippet']['title']))
            return results
        else:
            return []
    except requests.exceptions.RequestException as e:
        print(f"Error connecting to YouTube API: {e}")
        return []


def select_option(options, prompt):
    if fzf:
        fzf_command = f'echo "{options}" | fzf --prompt="{prompt}"'
        result = subprocess.run(fzf_command, shell=True, capture_output=True, text=True)
        selected_option = result.stdout.strip()
        if selected_option:
            # Extract the ID between the last pair of parentheses
            try:
                selected_id = selected_option.split('(')[-1].strip(')')
                return selected_id
            except IndexError:
                print("Failed to parse selected option.")
                return None
    else:
        # Fallback for when fzf is not installed
        options_list = options.split('\n')
        for i, option in enumerate(options_list, 1):
            print(f"{i}. {option}")
        try:
            choice = int(input(f"{prompt} (1-{len(options_list)}): "))
            if 1 <= choice <= len(options_list):
                selected_option = options_list[choice-1]
                selected_id = selected_option.split('(')[-1].strip(')')
                return selected_id
            else:
                print("Invalid choice.")
                return None
        except ValueError:
            print("Please enter a number.")
            return None
    return None

def get_video_url(video_id):
    ytdl_command = f'yt-dlp -f bestaudio --get-url {VIDEO_URL}{video_id}'
    result = subprocess.run(ytdl_command, shell=True, capture_output=True, text=True)
    return result.stdout.strip()

def is_mpv_installed():
    try:
        subprocess.run(['mpv', '--version'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)
        return True
    except FileNotFoundError:
        return False

def play_audio_with_mpv(video_id, title, loop=False):
    video_url = get_video_url(video_id)
    if video_url:
        try:
            mpv_command = [
                'mpv', '--no-video',
                '--cache=yes', '--cache-secs=3',
                f'--term-playing-msg=🎵 Now Playing: {title}\n',
                video_url
            ]
            if loop:
                mpv_command.insert(2, '--loop=inf')
            subprocess.run(mpv_command, check=False)
            subprocess.run(['clear'], check=False)
            return True
        except Exception as e:
            print(f"An error occurred while trying to play audio with MPV: {e}")
            return False
    else:
        print(f"Failed to get video URL for : {video_id}, {title}")
        return False

def play_audio_with_vlc(video_url, loop=False):
    try:
        # Extract the direct audio URL with yt-dlp
        ydl_opts = {
            'format': 'bestaudio/best',
            'quiet': True,
            'skip_download': True,
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(video_url, download=False)
            stream_url = info['url']  # Direct audio URL

        # Build VLC command
        vlc_path = r"C:\Program Files\VideoLAN\VLC\vlc.exe"
        vlc_command = [
            vlc_path,
            '--no-video',
            '--qt-start-minimized',
            '--play-and-exit',
            stream_url
        ]

        # Remove empty arguments
        vlc_command = [arg for arg in vlc_command if arg]
        subprocess.run(vlc_command, shell=False)

    except Exception as e:
        print(f"❌ An error occurred while trying to play audio with VLC: {e}")

def play_playlist(query, playlist_id):
    query = f'"{query}"'
    params = {
        'q': query,
        'part': 'snippet',
        'playlistId': playlist_id,
        'key': API_KEY,
        'maxResults': 15,
    }
    try:
        response = requests.get(PLAYLIST_URL, params=params)
        response.raise_for_status()
        data = response.json()

        if 'items' in data and len(data['items']) > 0:
            # Titre de la playlist (pas de la première vidéo) // 
            # To do ammeliorer cette partie du code pour la rendre efficace
            # Ca m'affiche le titre de la 1er vidéo pas le titre de la playliste 
            playlist_title = data['items'][0]['snippet']['title']
            
            # Collecte des vidéos de la playlist
            video_ids = [item['snippet']['resourceId']['videoId'] for item in data['items']]
            video_titles = [item['snippet']['title'] for item in data['items']]

            options = "\n".join([f"{title}" for title in video_titles])  # Titres des vidéos
            
            # Afficher le titre de la playlist
            print(f"Playlist: {playlist_title}")
            print("Videos in the playlist:")
            print(options)
            
            confirm = input("Do you want to play this playlist? (y/n): ")

            if confirm.lower() == 'y':
                for video_id, title in zip(video_ids, video_titles):
                    video_url = get_video_url(video_id)
                    if is_mpv_installed():
                        print(f"🎵 Now Playing: {title}")
                        play_audio_with_mpv(video_url, title, loop=False)
                    else:
                        print(f"🎵 Now Playing: {title}")
                        play_audio_with_vlc(video_url, title)
            else:
                print("[red]No videos found in the playlist.")
        else:
            print("[red]No videos found in the playlist.")
    except requests.exceptions.RequestException as e:
        print(f"Error fetching playlist: {e}")



def show_menu():
    menu_options = {
        1: '🔍 Search for a video',
        2: '📂 Search for a playlist',
        3: 'ℹ️ Help',
        4: '❌ Exit'
    }
    
    if fzf:
        options = "\n".join(menu_options.values())
        selected_option = select_option(options, "Select an option: ")
        # Try to match the selected_option with the menu values
        for num, text in menu_options.items():
            if selected_option == str(num) or selected_option in text:
                return str(num)
        return selected_option
    else:
        # Simple menu for terminal without fzf
        print("\n=== YouTube Audio Player ===")
        for num, text in menu_options.items():
            print(f"{num}. {text}")
        try:
            choice = int(input("Select an option (1-4): "))
            if 1 <= choice <= 4:
                return str(choice)
            else:
                print("Invalid choice. Please enter a number between 1 and 4.")
                return None
        except ValueError:
            print("Please enter a number.")
            return None

def show_help():
    help_text = """
    YouTube Audio Player Help:
    
    🔍 Search for a video: Search for a video on YouTube and play the audio.
    📂 Search for a playlist: Search for a playlist on YouTube and play the audio.
    ℹ️ Help: Show this help menu.
    ❌ Exit: Exit the application.
    
    Controls:
    - Use the arrow keys to navigate the menu.
    - Press Enter to select an option.
    - Press Esc to exit the menu.
    """
    print(help_text)
    wait = input("Press Enter to continue...")
    subprocess.run(['cls' if os.name == 'nt' else 'clear'], shell=True, check=False)

def get_search_query():
    if fzf:  # si fzf est installé
        # Utiliser fzf pour la saisie de la requête de recherche
        fzf_command = 'echo "" | fzf --print-query --prompt="Enter search query: " --header="YouTube Audio Player"'
        query = subprocess.run(fzf_command, shell=True, capture_output=True, text=True).stdout.strip()
    else:
        # Si fzf n'est pas installé, utiliser une saisie classique
        query = input("Enter search query: ").strip()
    return query