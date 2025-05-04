enable i2c through 
```
sudo raspi-config
```
Interface Options > I2C > Enable ARM I2C > yes

// stuff run

pip3 install adafruit-circuitpython-scd4x
sudo pip3 install adafruit-circuitpython-max9744 --break-system-packages
sudo pip3 install adafruit-circuitpython-seesaw --break-system-packages
pip3 install board

frank@raspberrypi:~ $ i2cdetect -y 1
     
     
     0  1  2  3  4  5  6  7  8  9  a  b  c  d  e  f
00:                         -- -- -- -- -- -- -- -- 
10: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- 
20: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- 
30: -- -- -- -- -- -- 36 -- -- -- -- -- -- -- -- -- 
40: -- -- -- -- -- -- -- -- -- -- -- 4b -- -- -- -- 
50: 50 -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- 
60: -- -- 62 -- -- -- -- -- -- -- -- -- -- -- -- -- 
70: -- -- -- -- -- -- -- --   

62: Audio amp
4b co2 snsor
50 display



https://avw.mdr.de/streams/284340-0_mp3_high.m3u