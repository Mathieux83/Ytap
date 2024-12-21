from utils import show_menu, get_search_query, search_youtube, select_option, play_audio, play_playlist, show_help

def main():
    while True:
        selected_option = show_menu()
        if selected_option == '🔍 Search for a video':
            while True:
                query = get_search_query()
                if query:
                    results = search_youtube(query, search_type='video')
                    if results:
                        options = "\n".join([f"{title} ({video_id})" for video_id, title in results])
                        selected_video_id = select_option(options, "Select a video: ")
                        if selected_video_id:
                            title = next(title for video_id, title in results if video_id == selected_video_id)
                            play_audio(selected_video_id, title, loop=False)
                        else:
                            print("No video selected.")
                            break
                    else:
                        print("No videos found for the query.")
                        break
                else:
                    print("No query entered.")
                    break
        elif selected_option == '📂 Search for a playlist':
            query = get_search_query()
            if query:
                results = search_youtube(query, search_type='playlist')
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
        elif selected_option == 'ℹ️ Help':
            show_help()
        elif selected_option == '❌ Exit':
            break
        else:
            print("Invalid option. Please try again.")

if __name__ == "__main__":
    main()