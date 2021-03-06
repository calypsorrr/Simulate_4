#!/usr/bin/env python
"""
Simulate 4 project
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
c.execute("SELECT database_id FROM notion WHERE id = 'youtube';")
results_youtube = c.fetchall()
id_youtube = results_youtube[0]
databaseId_youtube_sql = ''.join(id_youtube)
conn.close()

# path waar de folder gemaakt moet worden
path = "/home/pi/project_sim/logs"

# variablen facebook
token_f = access_token

# variabelen youtube
token = "AIzaSyCx8-hcIQdf7taEdK_IQ03MrY1EMfrayi0"

# variablen notion
databaseId_Youtube = databaseId_youtube_sql

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

readUrl = f"https://api.notion.com/v1/databases/{databaseId_Youtube}/query"
res = requests.request("POST", readUrl, headers=headers_post)
data = res.json()
youtube_insert_id = data["results"][0]["id"]

page_id_youtube = youtube_insert_id


def create_folder():
    try:
        os.mkdir(path)
    except FileExistsError:
        print("folder already exist")


def youtube_id():
    global data_url
    url_data = urlparse(url)
    data_url = url_data.query[2::]

    with open('logs/youtube_id.json', 'w', encoding='utf8') as f:
        json.dump(data_url, f, ensure_ascii=False)

def read_Youtube_video(data_url, token):
    data = urllib.request.urlopen(
        f"https://www.googleapis.com/youtube/v3/videos?part=statistics&id={data_url}&key={token}").read()
    viewcount = json.loads(data)["items"][0]["statistics"]["viewCount"]
    global converted_view
    converted_view = int(viewcount)

    with open('logs/youtube_views.json', 'w', encoding='utf8') as f:
        json.dump(converted_view, f, ensure_ascii=False)

def read_notion_Youtube_id(databaseId_youtube, headers_post):
    readUrl = f"https://api.notion.com/v1/databases/{databaseId_youtube}/query"

    res = requests.request("POST", readUrl, headers=headers_post)
    data = res.json()
    global views
    global goal
    global url
    views = data["results"][0]["properties"]["Views"]["number"]
    goal = data["results"][0]["properties"]["Goal"]["number"]
    url = data["results"][0]["properties"]["url youtube video"]["title"][0]["text"]["content"]

def update_notion_youtube(page_id_youtube, headers_patch):
    url = f"https://api.notion.com/v1/pages/{page_id_youtube}"

    updateData = {
        "properties": {
            "Views": {
                "id": "ETq%5C",
                "type": "number",
                "number": converted_view
            }
        }
    }

    data = json.dumps(updateData)
    response = requests.request("PATCH", url, headers=headers_patch, data=data)
    print(response)

def youtube_notion():
    disp.clear()
    draw.rectangle((0,0,width,height), outline=0, fill=0)
    draw.text((x + 30, top), "Youtube", font=font, font_size=30, fill=255)
    disp.image(image)
    disp.display()
    while True:
        create_folder()
        read_notion_Youtube_id(databaseId_Youtube, headers_post)
        youtube_id()
        read_Youtube_video(data_url, token)
        update_notion_youtube(page_id_youtube, headers_patch)
        if converted_view == goal:
            pixels.fill((255, 255, 255))
        elif converted_view <= goal/100*20:
            pixels[0] = (255, 255, 255)
        elif converted_view <= goal/100*40:
            pixels[0] = (255, 255, 255)
            pixels[1] = (255, 255, 255)
        elif converted_view <= goal/100*60:
            pixels[0] = (255, 255, 255)
            pixels[1] = (255, 255, 255)
            pixels[2] = (255, 255, 255)
        elif converted_view <= goal/100*80:
            pixels[0] = (255, 255, 255)
            pixels[1] = (255, 255, 255)
            pixels[2] = (255, 255, 255)
            pixels[3] = (255, 255, 255)
        time.sleep(100)


def main_1():
    disp.clear()
    pixels.fill((0, 0, 0))
    youtube_notion()


if __name__ == '__main__':  # code to execute if called from command-line
    main_1()
