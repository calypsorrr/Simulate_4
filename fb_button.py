#!/usr/bin/env python
"""
Info about our project comes here
"""

import requests
import urllib.request
import RPi.GPIO as GPIO
from gpiozero import Button
import json
import facebook
from urllib.parse import urlparse
import os
import board
import neopixel
import time
import Adafruit_GPIO.SPI as SPI
import Adafruit_SSD1306
from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont
import sqlite3
import subprocess

__author__ = "Bo Claes"
__email__ = "bo.claes@student.kdg.be"
__status__ = "Development"


# Raspberry Pi pin configuration:
RST = None
# Note the following are only used with SPI:
# DC = 23
# SPI_PORT = 0
# SPI_DEVICE = 0

# Beaglebone Black pin configuration:
# RST = 'P9_12'
# Note the following are only used with SPI:
# DC = 'P9_15'
# SPI_PORT = 1
# SPI_DEVICE = 0

# 128x32 display with hardware I2C:
disp = Adafruit_SSD1306.SSD1306_128_32(rst=RST)

# Initialize library.
disp.begin()

# Clear display.
disp.clear()
disp.display()

# Create blank image for drawing.
# Make sure to create image with mode '1' for 1-bit color.
width = disp.width
height = disp.height
image = Image.new('1', (width, height))

# Get drawing object to draw on image.
draw = ImageDraw.Draw(image)

padding = 10
shape_width = 30
top = padding
bottom = height-padding
x = padding

# Load default font.
font = ImageFont.load_default()

LED_COUNT = 5
pixels = neopixel.NeoPixel(board.D18,LED_COUNT)

conn = sqlite3.connect('fb.db')
c = conn.cursor()
c.execute("SELECT fbid FROM dhtreadings ORDER BY ROWID DESC LIMIT 1;")
results = c.fetchall()
id = results[0]
access_token = ''.join(id)
c.execute("SELECT database_id FROM notion WHERE id = 'facebook';")
results_facebook = c.fetchall()
id_facebook = results_facebook[0]
databaseId_facebook_sql = ''.join(id_facebook)
conn.close()

path = "/home/pi/project_sim/logs"

# variablen facebook
token_f = access_token

# variabelen youtube
token = "AIzaSyCx8-hcIQdf7taEdK_IQ03MrY1EMfrayi0"

# variablen notion
databaseId_facebook = databaseId_facebook_sql

headers_patch = {
    "Accept": "application/json",
    "Notion-Version": "2021-08-16",
    "Content-Type": "application/json",
    "Authorization": "Bearer secret_wzb2F3FIuFZWbqgTz5ppApmG7wm0nD5A6spmeAs7a0P"
}

headers_post = {
    "Accept": "application/json",
    "Notion-Version": "2021-08-16",
    "Authorization": "Bearer secret_wzb2F3FIuFZWbqgTz5ppApmG7wm0nD5A6spmeAs7a0P"
}

readUrl = f"https://api.notion.com/v1/databases/{databaseId_facebook}/query"
res = requests.request("POST", readUrl, headers=headers_post)
data = res.json()
fb_insert_id = data["results"][0]["id"]

page_id_facebook = fb_insert_id

def create_folder():
    try:
        os.mkdir(path)
    except FileExistsError:
        print("folder already exist")


def facebook_likes(token_f):
    graph = facebook.GraphAPI(token_f)
    fields = ["new_like_count"]
    profile = graph.get_object(fb_id, fields=fields)
    y = json.dumps(profile)
    x = json.loads(y)
    global fb_likes_2
    fb_likes_2 = (x["new_like_count"])

    with open('logs/facebook.json', 'w', encoding='utf8') as f:
        json.dump(profile, f, ensure_ascii=False)


def read_notion_facebook(databaseId_facebook, headers_post):
    readUrl = f"https://api.notion.com/v1/databases/{databaseId_facebook}/query"

    res = requests.request("POST", readUrl, headers=headers_post)
    data = res.json()
    global fb_goal
    global fb_likes
    global fb_id
    fb_goal = data["results"][0]["properties"]["Goal"]["number"]
    fb_likes = data["results"][0]["properties"]["Likes"]["number"]
    fb_id = data["results"][0]["properties"]["Facebook_id"]["title"][1]["text"]["content"]


def update_notion_facebook(page_id_facebook, headers_patch):
    url = f"https://api.notion.com/v1/pages/{page_id_facebook}"

    updateData = {
        "properties": {
            "Likes": {
                "id": "ETq%5C",
                "type": "number",
                "number": fb_likes_2
            }
        }
    }

    data = json.dumps(updateData)
    response = requests.request("PATCH", url, headers=headers_patch, data=data)
    print(response)


def facebook_notion():
    disp.clear()
    draw.rectangle((0,0,width,height), outline=0, fill=0)
    draw.text((x + 30, top), "Facebook", font=font, font_size=30, fill=255)
    disp.image(image)
    disp.display()
    while True:
        create_folder()
        read_notion_facebook(databaseId_facebook, headers_post)
        facebook_likes(token_f)
        update_notion_facebook(page_id_facebook, headers_patch)
        if fb_likes_2 == fb_goal:
            pixels.fill((255, 255, 255))
        elif fb_likes_2 <= fb_goal/100*20:
            pixels[0] = (255, 255, 255)
        elif fb_likes_2 <= fb_goal/100*40:
            pixels[0] = (255, 255, 255)
            pixels[1] = (255, 255, 255)
        elif fb_likes_2 <= fb_goal/100*60:
            pixels[0] = (255, 255, 255)
            pixels[1] = (255, 255, 255)
            pixels[2] = (255, 255, 255)
        elif fb_likes_2 <= fb_goal/100*80:
            pixels[0] = (255, 255, 255)
            pixels[1] = (255, 255, 255)
            pixels[2] = (255, 255, 255)
            pixels[3] = (255, 255, 255)
        time.sleep(100)




def main_2():
    disp.clear()
    pixels.fill((0, 0, 0))
    facebook_notion()



if __name__ == '__main__':  # code to execute if called from command-line
    main_2()
