#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import glob
import json
import os
import time
from sys import exit

from font_fredoka_one import FredokaOne
from PIL import Image, ImageDraw, ImageFont


"""
To run this example on Python 2.x you should:
    sudo apt install python-lxml
    sudo pip install geocoder requests font-fredoka-one

On Python 3.x:
    sudo apt install python3-lxml
    sudo pip3 install geocoder requests font-fredoka-one
"""

try:
    import requests
except ImportError:
    exit("This script requires the requests module\nInstall with: sudo pip install requests")

try:
    import geocoder
except ImportError:
    exit("This script requires the geocoder module\nInstall with: sudo pip install geocoder")

print("""Inky pHAT: Weather

Displays weather information for a given location. The default location is Sheffield-on-Sea.

""")

# Get the current path
PATH = os.path.dirname(__file__)

CITY = "Dublin"
COUNTRYCODE = "IR"
WARNING_TEMP = 25.0

white = (255, 255, 255, 255)
red = (255, 0, 0, 255)
black = (0, 0, 0, 255)

current_stream = "Tagesschau 100 Sekunden"

# Convert a city name and country code to latitude and longitude
def get_coords(address):
    g = geocoder.arcgis(address)
    coords = g.latlng
    return coords

# Query OpenMeteo (https://open-meteo.com) to get current weather data
def get_weather(address):
    coords = get_coords(address)
    weather = {}
    res = requests.get("https://api.open-meteo.com/v1/forecast?latitude=" + str(coords[0]) + "&longitude=" + str(coords[1]) + "&current_weather=true")
    if res.status_code == 200:
        j = json.loads(res.text)
        current = j["current_weather"]
        weather["temperature"] = current["temperature"]
        weather["windspeed"] = current["windspeed"]
        weather["weathercode"] = current["weathercode"]
        return weather
    else:
        return weather

def create_mask(source, mask=(white, black, red)):
    """Create a transparency mask.

    Takes a paletized source image and converts it into a mask
    permitting all the colours supported by Inky pHAT (0, 1, 2)
    or an optional list of allowed colours.

    :param mask: Optional list of Inky pHAT colours to allow.

    """
    mask_image = Image.new("1", source.size)
    w, h = source.size
    for x in range(w):
        for y in range(h):
            p = source.getpixel((x, y))
            if p in mask:
                mask_image.putpixel((x, y), 255)

    return mask_image


def draw_text_right_aligned(text, y, font, color):
    """Draw text right-aligned on the canvas."""
    text_bbox = font.getbbox(text)
    text_width = text_bbox[2] - text_bbox[0]  # Width of the text
    x_position = img.width - text_width - 5  # Right-aligned with a margin
    draw.text((x_position, y), text, color, font=font)

def draw_text_centered(text, y, font, color):
    """Draw text centered on the canvas."""
    text_bbox = font.getbbox(text)
    text_width = text_bbox[2] - text_bbox[0]  # Width of the text
    x_position = (img.width - text_width) // 2
    draw.text((x_position, y), text, color, font=font)

def get_text_height(font):
    """Get the height of the text using the font."""
    return font.getbbox("A")[3] - font.getbbox("A")[1]  # Height of the text

# Dictionaries to store our icons and icon masks in
icons = {}
masks = {}

# Get the weather data for the given location
location_string = "{city}, {countrycode}".format(city=CITY, countrycode=COUNTRYCODE)
weather = get_weather(location_string)

# This maps the weather code from Open Meteo
# to the appropriate weather icons
# Weather codes from https://open-meteo.com/en/docs
icon_map = {
    "snow": [71, 73, 75, 77, 85, 86],
    "rain": [51, 53, 55, 56, 57, 61, 63, 65, 66, 67, 80, 81, 82],
    "cloud": [1, 2, 3, 45, 48],
    "sun": [0],
    "storm": [95, 96, 99],
    "wind": []
}

# Placeholder variables
windspeed = 0.0
temperature = 0.0
weather_icon = None
device_temp = 25.4
device_co2 = 50.0
device_humidity = 75.0

if weather:
    temperature = weather["temperature"]
    windspeed = weather["windspeed"]
    weathercode = weather["weathercode"]

    for icon in icon_map:
        if weathercode in icon_map[icon]:
            weather_icon = icon
            break
else:
    print("Warning, no weather information found!")

# Create a new canvas to draw on
img = Image.open(os.path.join(PATH, "resources/backdrop2.png")).resize((212, 104))
draw = ImageDraw.Draw(img)

# Load our icon files and generate masks
for icon in glob.glob(os.path.join(PATH, "resources/icon-*.png")):
    icon_name = icon.split("icon-")[1].replace(".png", "")
    icon_image = Image.open(icon)
    icons[icon_name] = icon_image
    masks[icon_name] = create_mask(icon_image)

# Load the FredokaOne font
font = ImageFont.truetype(FredokaOne, 20)
font_small = ImageFont.truetype(FredokaOne, 16)

# Write text with weather values to the canvas
datetime = time.strftime("%d/%m %H:%M")
temperature_from_weather_string = str("{}°C".format(temperature))
device_temperature_string = str("{}°C".format(device_temp))
device_co2_string = str("{} ppm".format(int(device_co2)))
device_humidity_string = str("{}%".format(int(device_humidity)))


draw.text((0, 0), datetime, white, font=font)
weather_block_y = 46
draw_text_right_aligned(location_string, weather_block_y, font_small, white if temperature < WARNING_TEMP else red)
draw_text_right_aligned(temperature_from_weather_string, weather_block_y+1+get_text_height(font_small), font, white if temperature < WARNING_TEMP else red)

def draw_stacked_text_left_aligned(texts, y):
    """Draw stacked text left-aligned on the canvas."""
    for text, font, color in texts:
        text_bbox = font.getbbox(text)
        text_width = text_bbox[2] - text_bbox[0]  # Width of the text
        x_position = 5  # Left-aligned with a margin
        draw.text((x_position, y), text, color, font=font)
        y += get_text_height(font) + 1  # Move down for the next line


draw_stacked_text_left_aligned([( device_temperature_string, font, white),
                                (device_co2_string, font_small, white),
                                (device_humidity_string, font_small, white)],
                                35)


# Draw the current weather icon over the backdrop
if weather_icon is not None:
    #img.paste(icons[weather_icon], (28, 36), masks[weather_icon])
    img.paste(icons[weather_icon], (175, 0))

draw_text_centered(current_stream, 85, font_small, white)

# Draw the image to the screen
img.show()
