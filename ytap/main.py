from utils import *
import subprocess

def main():
    while True:
        selected_option = show_menu()
        
        # Convert selected_option to int if it's a number
        try:
            selected_option_num = int(selected_option)
        except (ValueError, TypeError):
            selected_option_num = None
            
        # Check both string representation and numeric value
        if selected_option == '🔍 Search for a video' or selected_option_num == 1:
            while True:
                query = get_search_query()
                if query:
                    results = search_youtube(query, search_type='video')
                    if results:
                        options = "\n".join([f"{title} ({video_id})" for video_id, title in results])
                        selected_video_id = select_option(options, "Select a video: ")
                        if selected_video_id:
                            title = next(title for video_id, title in results if video_id == selected_video_id)
                            # Prevent error if MPV is not installed
                            if not is_mpv_installed():
                            # If no MPV, play with VLC
                                print("Lecture de :", title, "en cours...")
                                play_audio_with_vlc(selected_video_id, title)  # Play with VLC
                            else:
                                print("Lecture de :", title, "en cours...")
                                play_audio_with_mpv(selected_video_id, title, loop=False)
                    else:
                        print("No videos found for the query.")
                        break
                else:
                    print("No query entered.")
                    break
        
        elif selected_option == '📂 Search for a playlist' or selected_option_num == 2:
            query = get_search_query()
            if query:
                results = search_youtube(query, search_type='playlist')
                if results:
                    options = "\n".join([f"{title} ({playlist_id})" for playlist_id, title in results])
                    selected_playlist_id = select_option(options, "Select a playlist: ")
                    if selected_playlist_id:
                        play_playlist(query, selected_playlist_id)  # Pass query here too
                    else:
                        print("No playlist selected.")
                else:
                    print("No playlists found for the query.")
            else:
                print("No query entered.")
        
        elif selected_option == 'ℹ️ Help' or selected_option_num == 3:
            show_help()
        elif selected_option == '❌ Exit' or selected_option_num == 4:
            print("Exiting the application...")
            break
        else:
            print("Invalid option. Please try again.")

if __name__ == "__main__":
    main()
