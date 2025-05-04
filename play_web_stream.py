import vlc
import time

def play_stream(url):
    # Create a VLC instance and media list player
    instance = vlc.Instance()
    media_list = instance.media_list_new([url])
    player = instance.media_list_player_new()
    player.set_media_list(media_list)
    
    # Start playing the stream
    print(f"Playing stream: {url}")
    player.play()
    
    # Wait for the player to initialize
    time.sleep(2)  # Give VLC some time to start playing
    
    # Check if the player is playing
    if player.get_state() == vlc.State.Playing:
        print("Audio is playing...")
    else:
        print("Failed to play the audio. Please check the stream URL or VLC installation.")
    
    # Keep the program running while the stream plays
    try:
        while True:
            time.sleep(1)  # Prevent high CPU usage
    except KeyboardInterrupt:
        print("\nStopping playback.")
        player.stop()

if __name__ == "__main__":
    stream_url = "https://avw.mdr.de/streams/284340-0_mp3_high.m3u"
    play_stream(stream_url)