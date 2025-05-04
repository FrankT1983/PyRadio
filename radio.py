import time
import board
import busio
import adafruit_max9744
from adafruit_seesaw.seesaw import Seesaw
from adafruit_seesaw import rotaryio, digitalio, neopixel

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


while True:    
    position1 = -encoder1.position
    position2 = -encoder2.position
    

    if last_position1 is None:
        last_position1 = position1

    if position1 != last_position1:
        positino1_delta =  last_position1 - position1
        last_position1 = position1
        print("Position 1: {}".format(position1))
        print("Position delate 1: {}".format(positino1_delta))

        if (abs(positino1_delta)> 10) :
            positino1_delta = 0
        
        audio_volume += positino1_delta
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
        print("Button 1 released")  


