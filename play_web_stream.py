from pynput import keyboard  # Replacing the keyboard package
import vlc
import time
import requests
import xml.etree.ElementTree as ET

playing_something = False
current_index = 0
key_pressed = None

def on_press(key):
    global key_pressed
    try:
        key_pressed = key.char  # Get the character of the key pressed
    except AttributeError:
        pass  # Handle special keys like Shift, Ctrl, etc.

def on_release(key):
    global key_pressed
    key_pressed = None  # Reset the key when released

def get_mp3_url_from_rss(rss_url):
    try:
        response = requests.get(rss_url)
        response.raise_for_status()
        root = ET.fromstring(response.content)
        for item in root.findall(".//item"):
            enclosure = item.find("enclosure")
            if enclosure is not None:
                url = enclosure.get("url")
                file_type = enclosure.get("type")
                if file_type == "audio/mpeg" and url.endswith(".mp3"):
                    return url
        return None
    except requests.RequestException as e:
        print(f"Error fetching RSS feed: {e}")
        return None
    except ET.ParseError as e:
        print(f"Error parsing XML: {e}")

def switch_stream(player, news_player, streams, new_index):
    global playing_something
    news_player.stop()
    player.play_item_at_index(new_index)
    playing_something = True
    print(f"Switched to stream: {streams[new_index]['name']} ({streams[new_index]['url']})")

def play_streams(streams, news_streams):
    global playing_something, current_index, key_pressed
    instance = vlc.Instance()
    player = instance.media_list_player_new()
    media_list = instance.media_list_new([stream["url"] for stream in streams])
    player.set_media_list(media_list)
    news_player = instance.media_player_new()
    switch_stream(player, news_player, streams, current_index)

    listener = keyboard.Listener(on_press=on_press, on_release=on_release)
    listener.start()

    try:
        while True:
            if key_pressed == 'a':
                current_index = (current_index - 1) % len(streams)
                switch_stream(player, news_player, streams, current_index)
                time.sleep(1)

            if key_pressed == 'd':
                current_index = (current_index + 1) % len(streams)
                switch_stream(player, news_player, streams, current_index)
                time.sleep(1)

            if key_pressed == 'p':
                if playing_something:
                    print("Stopping playback.")
                    player.stop()
                    news_player.stop()
                    playing_something = False
                else:
                    switch_stream(player, news_player, streams, current_index)

            if key_pressed == 'n':
                news_url = get_mp3_url_from_rss(news_streams[0]["rss"])
                if news_url:
                    print(f"Playing news: {news_streams[0]['name']} ({news_url})")
                    news_player.set_media(instance.media_new(news_url))
                    playing_something = True
                    player.stop()
                    news_player.play()
                    time.sleep(1)

            time.sleep(0.1)
    except KeyboardInterrupt:
        print("\nStopping playback.")
        player.stop()
        news_player.stop()
    finally:
        listener.stop()

if __name__ == "__main__":
    streams = [
        {"name": "MDR", "url": "https://avw.mdr.de/streams/284340-0_mp3_high.m3u"},
        {"name": "MDR Sputnik", "url": "https://avw.mdr.de/streams/284331-1_mp3_high.m3u"}
    ]

    news_streams = [
        {"name": "Tagesschau 100 Sekunden", "rss": "https://www.tagesschau.de/multimedia/sendung/tagesschau_in_100_sekunden/podcast-ts100-audio-100~podcast.xml"},
    ]
    play_streams(streams, news_streams)