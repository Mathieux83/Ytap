import requests
import subprocess
import sys
import os
from pathlib import Path
from rich.progress import Progress
from rich.console import Console as console
import time

# Définir le chemin du fichier API_KEY en fonction du répertoire du projet
BASE_DIR = Path(__file__).resolve().parent
API_KEY_FILE_PATH = BASE_DIR / 'API_KEY'

# Lire la clé API depuis le fichier config/API_KEY
try:
    with open(API_KEY_FILE_PATH, 'r') as file:
        API_KEY = file.read().strip()
except FileNotFoundError:
    console.print("[red]API_KEY file not found. Please create an API_KEY file with your YouTube API key.")
    sys.exit(1)
except Exception as e:
    console.print(f"[red]An error occurred while reading the API_KEY file: {e}")
    sys.exit(1)

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
    response = requests.get(SEARCH_URL, params=params)
    data = response.json()

    if 'items' in data and len(data['items']) > 0:
        if search_type == 'playlist':
            results = [(item['id']['playlistId'], item['snippet']['title']) for item in data['items']]
        else:
            results = [(item['id'][f'{search_type}Id'], item['snippet']['title']) for item in data['items']]
        return results
    else:
        return []

def select_option(options, prompt):
    fzf_command = f'echo "{options}" | fzf --prompt="{prompt}"'
    selected_option = subprocess.run(fzf_command, shell=True, capture_output=True, text=True).stdout.strip()
    if selected_option:
        selected_id = selected_option.split('(')[-1].strip(')')
        return selected_id
    return None

def get_video_url(video_id):
    ytdl_command = f'yt-dlp -f bestaudio --get-url {VIDEO_URL}{video_id}'
    result = subprocess.run(ytdl_command, shell=True, capture_output=True, text=True)
    return result.stdout.strip()

def play_audio(video_id, title, loop=False):
    video_url = get_video_url(video_id)
    if video_url:
        mpv_command = [
            'mpv', '--no-video',
            f'--term-playing-msg=🎵 Now Playing: {title}',
            video_url
        ]
        if loop:
            mpv_command.insert(2, '--loop=inf')

        with Progress() as progress:
            task = progress.add_task(f"[green]Playing {title}...", total=100)
            process = subprocess.Popen(mpv_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            while process.poll() is None:
                progress.update(task, advance=1)
                time.sleep(1)

        subprocess.run(['clear'])
    else:
        print("Failed to retrieve video URL.")

def play_playlist(playlist_id):
    params = {
        'part': 'snippet',
        'playlistId': playlist_id,
        'key': API_KEY,
        'maxResults': 50
    }
    response = requests.get(PLAYLIST_URL, params=params)
    data = response.json()

    if 'items' in data and len(data['items']) > 0:
        video_ids = [item['snippet']['resourceId']['videoId'] for item in data['items']]
        video_titles = [item['snippet']['title'] for item in data['items']]
        options = "\n".join([f"{title} ({video_id})" for video_id, title in zip(video_ids, video_titles)])
        
        # Afficher la liste des vidéos de la playlist et attendre la validation de l'utilisateur
        print("Playlist selected:")
        print(options)
        confirm = input("Do you want to play this playlist? (y/n): ")
        
        if confirm.lower() == 'y':
            for video_id, title in zip(video_ids, video_titles):
                play_audio(video_id, title, loop=False)
        else:
            console.print("[yellow]Playlist playback cancelled.")
    else:
        console.print("[red]No videos found in the playlist.")

def show_menu():
    menu_options = [
        '🔍 Search for a video',
        '📂 Search for a playlist',
        'ℹ️ Help',
        '❌ Exit'
    ]
    options = "\n".join(menu_options)
    selected_option = select_option(options, "Select an option: ")
    return selected_option

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
    subprocess.run(['clear'])

def get_search_query():
    fzf_command = 'echo "" | fzf --print-query --prompt="Enter search query: " --header="YouTube Audio Player"'
    query = subprocess.run(fzf_command, shell=True, capture_output=True, text=True).stdout.strip()
    return query

