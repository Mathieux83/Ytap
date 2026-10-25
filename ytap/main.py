import argparse
from getpass import getpass

from . import __version__
from .config import load_api_key, save_api_key
from .utils import (
    get_search_query,
    is_mpv_installed,
    is_vlc_installed,
    play_audio_with_mpv,
    play_audio_with_vlc,
    play_playlist,
    search_youtube,
    select_option,
    show_help,
    show_menu,
)


def _configure():
    api_key = getpass("YouTube Data API v3 key: ")
    try:
        save_api_key(api_key)
    except (OSError, ValueError) as error:
        print(f"Could not save the API key: {error}")
        return
    print("API key saved.")


def _play_video(video_id, title):
    print(f"Now Playing: {title}")
    if is_mpv_installed():
        play_audio_with_mpv(video_id, title, loop=False)
    elif is_vlc_installed():
        play_audio_with_vlc(video_id, title, loop=False)
    else:
        print("No supported player found. Install mpv or VLC to play audio.")


def _run_player():
    while True:
        selected_option = show_menu()

        if selected_option == "1":
            while True:
                query = get_search_query()
                if query:
                    results = search_youtube(query, search_type="video")
                    if results:
                        options = "\n".join([f"{title} ({video_id})" for video_id, title in results])
                        selected_video_id = select_option(options, "Select a video: ")
                        if selected_video_id:
                            title = next(title for video_id, title in results if video_id == selected_video_id)
                            _play_video(selected_video_id, title)
                    else:
                        print("No videos found for the query.")
                        break
                else:
                    print("No query entered.")
                    break

        elif selected_option == "2":
            query = get_search_query()
            if query:
                results = search_youtube(query, search_type="playlist")
                if results:
                    options = "\n".join([f"{title} ({playlist_id})" for playlist_id, title in results])
                    selected_playlist_id = select_option(options, "Select a playlist: ")
                    if selected_playlist_id:
                        play_playlist(selected_playlist_id)
                    else:
                        print("No playlist selected.")
                else:
                    print("No playlists found for the query.")
            else:
                print("No query entered.")

        elif selected_option == "3":
            show_help()
        elif selected_option == "4":
            print("Exiting the application...")
            break
        else:
            print("Invalid option. Please try again.")


def main(argv=None):
    parser = argparse.ArgumentParser(description="Search YouTube and play audio.")
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    parser.add_argument("command", nargs="?", choices=("configure",))
    args = parser.parse_args(argv)

    if args.command == "configure":
        _configure()
        return
    if not load_api_key():
        print("No YouTube API key configured. Run 'ytap configure' to set it up.")
        return
    _run_player()


if __name__ == "__main__":
    main()
