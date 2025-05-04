import vlc
import time
import keyboard  # For detecting key presses
import requests
import xml.etree.ElementTree as ET


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

    news_streams = [
        {"name": "Tagesschau 100 Sekunden", "rss": "hhttps://www.tagesschau.de/multimedia/sendung/tagesschau_in_100_sekunden/podcast-ts100-audio-100~podcast.xml"},
    ]
    play_streams(streams)