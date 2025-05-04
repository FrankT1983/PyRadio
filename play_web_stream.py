import vlc
import time
import keyboard  # For detecting key presses

def play_streams(streams):
    # Create a VLC instance and media list player
    instance = vlc.Instance()
    player = instance.media_list_player_new()
    media_list = instance.media_list_new([stream["url"] for stream in streams])
    player.set_media_list(media_list)

    # Start playing the first stream
    current_index = 0
    player.play_item_at_index(current_index)
    print(f"Playing stream: {streams[current_index]['name']} ({streams[current_index]['url']})")

    try:
        while True:
            # Listen for 'a' to go to the previous stream
            if keyboard.is_pressed('a'):
                current_index = (current_index - 1) % len(streams)
                player.play_item_at_index(current_index)
                print(f"Switched to stream: {streams[current_index]['name']} ({streams[current_index]['url']})")
                time.sleep(1)  # Prevent rapid switching

            # Listen for 'd' to go to the next stream
            if keyboard.is_pressed('d'):
                current_index = (current_index + 1) % len(streams)
                player.play_item_at_index(current_index)
                print(f"Switched to stream: {streams[current_index]['name']} ({streams[current_index]['url']})")
                time.sleep(1)  # Prevent rapid switching

            time.sleep(0.1)  # Prevent high CPU usage
    except KeyboardInterrupt:
        print("\nStopping playback.")
        player.stop()

if __name__ == "__main__":
    streams = [
        {"name": "MDR", "url": "https://avw.mdr.de/streams/284340-0_mp3_high.m3u"},
        {"name": "MDR Sputnik", "url": "https://avw.mdr.de/streams/284331-1_mp3_high.m3u"}
    ]
    play_streams(streams)