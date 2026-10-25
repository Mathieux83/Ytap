import os
import shutil
import subprocess

import requests
import yt_dlp

from .config import load_api_key

SEARCH_URL = "https://www.googleapis.com/youtube/v3/search"
PLAYLIST_URL = "https://www.googleapis.com/youtube/v3/playlistItems"


def search_youtube(query, search_type="video", event_type=None):
    api_key = load_api_key()
    if not api_key:
        print("No YouTube API key configured. Run 'ytap configure' first.")
        return []

    params = {
        "part": "snippet",
        "q": query,
        "key": api_key,
        "maxResults": 20,
        "type": search_type,
    }
    if event_type:
        params["eventType"] = event_type

    try:
        response = requests.get(SEARCH_URL, params=params, timeout=15)
        response.raise_for_status()
        items = response.json().get("items", [])
        id_key = "playlistId" if search_type == "playlist" else f"{search_type}Id"
        return [
            (item["id"][id_key], item["snippet"]["title"])
            for item in items
            if id_key in item.get("id", {})
        ]
    except requests.exceptions.RequestException as error:
        print(f"Error connecting to YouTube API: {error}")
        return []


def _selected_value(option):
    _, separator, identifier = option.rpartition(" (")
    if separator and identifier.endswith(")"):
        return identifier[:-1]
    return option


def select_option(options, prompt):
    fzf_path = shutil.which("fzf")
    if fzf_path:
        result = subprocess.run(
            [fzf_path, "--prompt", prompt],
            input=options,
            capture_output=True,
            text=True,
            check=False,
        )
        if result.returncode == 0 and result.stdout.strip():
            return _selected_value(result.stdout.strip())
        return None

    options_list = options.splitlines()
    for index, option in enumerate(options_list, 1):
        print(f"{index}. {option}")
    try:
        choice = int(input(f"{prompt} (1-{len(options_list)}): "))
    except ValueError:
        print("Please enter a number.")
        return None
    if 1 <= choice <= len(options_list):
        return _selected_value(options_list[choice - 1])
    print("Invalid choice.")
    return None


def get_video_url(video_id):
    video_url = f"https://www.youtube.com/watch?v={video_id}"
    options = {
        "format": "bestaudio/best",
        "quiet": True,
        "no_warnings": True,
        "noplaylist": True,
    }
    try:
        with yt_dlp.YoutubeDL(options) as downloader:
            info = downloader.extract_info(video_url, download=False)
        return info.get("url", "") if info else ""
    except yt_dlp.utils.DownloadError as error:
        print(f"Failed to retrieve audio URL for {video_id}: {error}")
        return ""


def is_mpv_installed():
    return shutil.which("mpv") is not None


def get_vlc_path():
    configured_path = os.environ.get("YTAP_VLC_PATH")
    if configured_path:
        path = os.path.expandvars(os.path.expanduser(configured_path))
        if os.path.isfile(path) and (os.name == "nt" or os.access(path, os.X_OK)):
            return path
        return None

    vlc_path = shutil.which("vlc")
    if vlc_path:
        return vlc_path

    if os.name == "nt":
        for variable in ("ProgramFiles", "ProgramFiles(x86)"):
            program_files = os.environ.get(variable)
            if program_files:
                candidate = os.path.join(program_files, "VideoLAN", "VLC", "vlc.exe")
                if os.path.isfile(candidate):
                    return candidate
    return None


def is_vlc_installed():
    return get_vlc_path() is not None


def play_audio_with_mpv(video_id, title, loop=False):
    mpv_path = shutil.which("mpv")
    if not mpv_path:
        print("mpv is not installed or is not available on PATH.")
        return False
    video_url = get_video_url(video_id)
    if not video_url:
        print(f"Failed to get an audio URL for {video_id} ({title}).")
        return False

    command = [
        mpv_path,
        "--no-video",
        "--cache=yes",
        "--cache-secs=3",
        f"--term-playing-msg=Now Playing: {title}",
    ]
    if loop:
        command.append("--loop=inf")
    command.append(video_url)

    try:
        result = subprocess.run(command, check=False)
    except OSError as error:
        print(f"An error occurred while starting mpv: {error}")
        return False
    return result.returncode == 0


def play_audio_with_vlc(video_id, title, loop=False):
    vlc_path = get_vlc_path()
    if not vlc_path:
        print("VLC is not installed or could not be found. Set YTAP_VLC_PATH if needed.")
        return False

    video_url = get_video_url(video_id)
    if not video_url:
        print(f"Failed to get an audio URL for {video_id} ({title}).")
        return False

    command = [vlc_path, "--no-video", "--play-and-exit"]
    if loop:
        command.append("--repeat")
    command.append(video_url)
    try:
        result = subprocess.run(command, check=False)
    except OSError as error:
        print(f"An error occurred while starting VLC: {error}")
        return False
    return result.returncode == 0


def play_playlist(playlist_id):
    api_key = load_api_key()
    if not api_key:
        print("No YouTube API key configured. Run 'ytap configure' first.")
        return

    params = {
        "part": "snippet",
        "playlistId": playlist_id,
        "key": api_key,
        "maxResults": 50,
    }
    try:
        response = requests.get(PLAYLIST_URL, params=params, timeout=15)
        response.raise_for_status()
        items = response.json().get("items", [])
    except requests.exceptions.RequestException as error:
        print(f"Error fetching playlist: {error}")
        return

    videos = [
        (item["snippet"]["resourceId"]["videoId"], item["snippet"]["title"])
        for item in items
        if item.get("snippet", {}).get("resourceId", {}).get("videoId")
    ]
    if not videos:
        print("No videos found in the playlist.")
        return

    print(f"Playlist: {playlist_id}")
    print("Videos in the playlist:")
    for _, title in videos:
        print(title)
    if input("Do you want to play this playlist? (y/n): ").strip().lower() != "y":
        return

    player = play_audio_with_mpv if is_mpv_installed() else play_audio_with_vlc
    for video_id, title in videos:
        print(f"Now Playing: {title}")
        player(video_id, title, loop=False)


def show_menu():
    menu_options = {
        1: "🔍 Search for a video",
        2: "📂 Search for a playlist",
        3: "ℹ️ Help",
        4: "❌ Exit",
    }
    if shutil.which("fzf"):
        options = "\n".join(menu_options.values())
        selected_option = select_option(options, "Select an option: ")
        for number, label in menu_options.items():
            if selected_option == str(number) or selected_option == label:
                return str(number)
        return selected_option

    print("\n=== YouTube Audio Player ===")
    for number, label in menu_options.items():
        print(f"{number}. {label}")
    try:
        choice = int(input("Select an option (1-4): "))
    except ValueError:
        print("Please enter a number.")
        return None
    if 1 <= choice <= 4:
        return str(choice)
    print("Invalid choice. Please enter a number between 1 and 4.")
    return None


def show_help():
    print(
        """
YouTube Audio Player Help:

Search for a video or playlist on YouTube and play its audio.
fzf is optional; without it, use the numbered terminal menus.
"""
    )
    input("Press Enter to continue...")
    subprocess.run(["cls" if os.name == "nt" else "clear"], check=False)


def get_search_query():
    fzf_path = shutil.which("fzf")
    if fzf_path:
        result = subprocess.run(
            [
                fzf_path,
                "--print-query",
                "--prompt",
                "Enter search query: ",
                "--header",
                "YouTube Audio Player",
            ],
            input="",
            capture_output=True,
            text=True,
            check=False,
        )
        if result.stdout:
            return result.stdout.splitlines()[0].strip()
        return ""
    return input("Enter search query: ").strip()
