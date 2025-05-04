import time
import board
import busio
import adafruit_max9744
from adafruit_seesaw.seesaw import Seesaw
from adafruit_seesaw import rotaryio, digitalio, neopixel
import vlc
import time
import keyboard  # For detecting key presses
import requests
import xml.etree.ElementTree as ET

i2c = busio.I2C(board.SCL, board.SDA)
amp = adafruit_max9744.MAX9744(i2c)

i2c_bus = board.I2C()  # uses board.SCL and board.SDA

qt_enc1 = Seesaw(i2c, addr=0x36)
qt_enc2 = Seesaw(i2c, addr=0x37)

qt_enc1.pin_mode(24, qt_enc1.INPUT_PULLUP)
button1 = digitalio.DigitalIO(qt_enc1, 24)
button_held1 = False

qt_enc2.pin_mode(24, qt_enc2.INPUT_PULLUP)
button2 = digitalio.DigitalIO(qt_enc2, 24)
button_held2 = False

encoder1 = rotaryio.IncrementalEncoder(qt_enc1)
last_position1 = None

encoder2 = rotaryio.IncrementalEncoder(qt_enc2)
last_position2 = None

#pixel2 = neopixel.NeoPixel(qt_enc2, 6, 1)
#pixel2.brightness = 0.2
#pixel2.fill(0x0000ff)


audio_volume = 30
last_audio_volume = audio_volume
amp.volume = audio_volume




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
    is_muted = False
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
    key_wait = 0.1


    while True:
        try:
            position1 = -encoder1.position
            position2 = -encoder2.position        

            pressed_next = False
            pressed_prev = False
            pressed_channel = False

            pressed_mute = False

            volume_delta = 0

            # Handle volume up and down        
            if last_position1 is None:
                last_position1 = position1

            if position1 != last_position1:
                position1_delta =  last_position1 - position1
                last_position1 = position1
            
                if (abs(position1_delta)> 10) :
                    position1_delta = 0
                
                audio_volume += position1_delta
                if (audio_volume > 60):
                    audio_volume = 60

                if (audio_volume < 0):
                    audio_volume = 00
                    
                if audio_volume != last_audio_volume:
                    print("New Volume: {}".format(audio_volume))
                    last_audio_volume = audio_volume  
                    amp.volume = audio_volume


            if not button1.value and not button_held1:
                button_held1 = True        
                print("Button 1 pressed")

            if button1.value and button_held1:
                button_held1 = False        
                if is_muted:
                    print("Unmuting")
                    is_muted = False
                    amp.volume = audio_volume
                else:
                    print("Muting")
                    is_muted = True
                    amp.volume = 0        


            # Handle channel changing
            if last_position2 is None:
                last_position2 = position2

            if position2 != last_position2:
                position2_delta =  last_position2 - position2
                last_position2 = position2

                if (abs(position2_delta)> 10) :
                    position2_delta = 0

                if position2_delta > 0:
                    pressed_next = True              
                    print("Next channel")
                elif position2_delta < 0:
                    pressed_prev = True
                    print("Previous channel")

            if not button2.value and not button_held2:
                button_held2 = True        
                print("Button 2 pressed")

            if button2.value and button_held2:
                button_held2 = False        
                pressed_channel = True
                print("Channel button released")

            # Listen for 'a' to go to the previous stream
            if keyboard.is_pressed('a') or pressed_prev:
                current_index = (current_index - 1) % len(streams)
                switch_stream(player, news_player, streams, current_index)
                time.sleep(key_wait)  # Prevent rapid switching

            # Listen for 'd' to go to the next stream
            if keyboard.is_pressed('d') or pressed_next:
                current_index = (current_index + 1) % len(streams)
                switch_stream(player, news_player, streams, current_index)
                time.sleep(key_wait)  # Prevent rapid switching
            
            # Listen for 'p' to pause or resume playback
            if keyboard.is_pressed('p'):
                print("Pausing playback." + str(current_index) + " " + str(playing_something)) 
                if playing_something:
                    print("Stopping playback.")
                    player.stop()
                    news_player.stop()
                    playing_something = False
                else:
                    switch_stream(player, news_player, streams, current_index)                

            # Listen for 'n' to play news
            if keyboard.is_pressed('n') or pressed_channel:
                news_url = get_mp3_url_from_rss(news_streams[0]["rss"])
                if news_url:
                    print(f"Playing news: {news_streams[0]['name']} ({news_url})")
                    news_player.set_media(instance.media_new(news_url))
                    playing_something = True
                    player.stop()
                    news_player.play()
                    time.sleep(key_wait)

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




   


