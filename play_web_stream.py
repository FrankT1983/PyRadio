import vlc
import time
import keyboard  # For detecting key presses
import requests
import xml.etree.ElementTree as ET


playing_something = False

def get_mp3_url_from_rss(rss_url):
    try:
        # Fetch the RSS feed
        response = requests.get(rss_url)
        response.raise_for_status()  # Raise an error for HTTP issues

        # Parse the XML content
        root = ET.fromstring(response.content)

        # Find the first <item> element
        for item in root.findall(".//item"):
            # Extract the <enclosure> element
            enclosure = item.find("enclosure")
            if enclosure is not None:
                url = enclosure.get("url")
                file_type = enclosure.get("type")

                # Check if the file is an MP3
                if file_type == "audio/mpeg" and url.endswith(".mp3"):
                    return url

        return None  # Return None if no valid MP3 URL is found

    except requests.RequestException as e:
        print(f"Error fetching RSS feed: {e}")
        return None
    except ET.ParseError as e:
        print(f"Error parsing XML: {e}")

def switch_stream(player, news_player, streams, new_index,):
    global playing_something
    """Switch to a new stream by index."""
    news_player.stop()
    player.play_item_at_index(new_index)
    playing_something = True
    print(f"Switched to stream: {streams[new_index]['name']} ({streams[new_index]['url']})")


def play_streams(streams, news_streams):
    global playing_something
    # Create a VLC instance and media list player
    instance = vlc.Instance()
    player = instance.media_list_player_new()
    media_list = instance.media_list_new([stream["url"] for stream in streams])
    player.set_media_list(media_list)

    # Create a separate MediaPlayer for news streams
    news_player = instance.media_player_new()

    # Start playing the first stream
    current_index = 0
    switch_stream(player, news_player, streams, current_index)

    try:
        while True:
            # Listen for 'a' to go to the previous stream
            if keyboard.is_pressed('a'):
                current_index = (current_index - 1) % len(streams)
                switch_stream(player, news_player, streams, current_index)
                time.sleep(1)  # Prevent rapid switching

            # Listen for 'd' to go to the next stream
            if keyboard.is_pressed('d'):
                current_index = (current_index + 1) % len(streams)
                switch_stream(player, news_player, streams, current_index)
                time.sleep(1)  # Prevent rapid switching
            
            if keyboard.is_pressed('p'):
                print("Pausing playback." + str(current_index) + " " + str(playing_something)) 
                if playing_something:
                    print("Stopping playback.")
                    player.stop()
                    news_player.stop()
                    playing_something = False
                else:
                    switch_stream(player, news_player, streams, current_index)                

            if keyboard.is_pressed('n'):
                news_url = get_mp3_url_from_rss(news_streams[0]["rss"])
                if news_url:
                    print(f"Playing news: {news_streams[0]['name']} ({news_url})")
                    news_player.set_media(instance.media_new(news_url))
                    playing_something = True
                    player.stop()
                    news_player.play()
                    time.sleep(1)


            time.sleep(0.1)  # Prevent high CPU usage
    except KeyboardInterrupt:
        print("\nStopping playback.")
        player.stop()
        news_player.stop()

if __name__ == "__main__":
    streams = [
        {"name": "MDR", "url": "https://avw.mdr.de/streams/284340-0_mp3_high.m3u"},
        {"name": "MDR Sputnik", "url": "https://avw.mdr.de/streams/284331-1_mp3_high.m3u"}
    ]

    news_streams = [
        {"name": "Tagesschau 100 Sekunden", "rss": "https://www.tagesschau.de/multimedia/sendung/tagesschau_in_100_sekunden/podcast-ts100-audio-100~podcast.xml"},
    ]
    play_streams(streams, news_streams)