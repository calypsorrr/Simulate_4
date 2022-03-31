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

# variabelen led's, buttons
button_1 = Button(pin=21)
button_2 = Button(pin=12)
button_3 = Button(pin=26)

LED_COUNT = 10
pixels = neopixel.NeoPixel(board.D18,LED_COUNT)

keyFile = open('fb.txt', 'r')
access_token = keyFile.readline().rstrip()

# path waar de folder gemaakt moet worden
path = "/home/pi/project_sim/logs"

# variablen facebook
token_f = access_token

# variabelen youtube
token = "AIzaSyCx8-hcIQdf7taEdK_IQ03MrY1EMfrayi0"

# variablen notion
databaseId_Youtube = "5c6c26485a5a48b8828e6754a4843745"
databaseId_facebook = "5a136948544c46cc8e0f12a6fe38ff59"
page_id_youtube = "a8c70dee-2b65-4ec0-bee8-95a7431a9365"
page_id_facebook = "e1443adb-e273-4814-ad2f-0dbfcb3bf9b2"

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

    with open('logs/notion_facebook.json', 'w', encoding='utf8') as f:
        json.dump(data, f, ensure_ascii=False)


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
    print(response.text)


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
    print(response.text)


def youtube_notion():
    disp.clear()
    draw.rectangle((0,0,width,height), outline=0, fill=0)
    draw.text((x + 30, top), "Youtube", font=font, font_size=30, fill=255)
    disp.image(image)
    disp.display()
    while True:
        print("u bent nu in youtube")
        create_folder()
        read_notion_Youtube_id(databaseId_Youtube, headers_post)
        youtube_id()
        read_Youtube_video(data_url, token)
        update_notion_youtube(page_id_youtube, headers_patch)
        if converted_view == goal:
            print("goal reached")
            pixels.fill((255, 255, 255))
        elif converted_view <= goal/100*10:
            print("tussen 0-10%")
            pixels[0] = (255, 255, 255)
        elif converted_view <= goal/100*20:
            print("tussen 10-20%")
            pixels[0] = (255, 255, 255)
            pixels[1] = (255, 255, 255)
        elif converted_view <= goal/100*30:
            print("tussen 20-30%")
            pixels[0] = (255, 255, 255)
            pixels[1] = (255, 255, 255)
            pixels[2] = (255, 255, 255)
        elif converted_view <= goal/100*40:
            print("tussen 30-40%")
            pixels[0] = (255, 255, 255)
            pixels[1] = (255, 255, 255)
            pixels[2] = (255, 255, 255)
            pixels[3] = (255, 255, 255)
        elif converted_view <= goal/100*50:
            print("tussen 40-50%")
            pixels[0] = (255, 255, 255)
            pixels[1] = (255, 255, 255)
            pixels[2] = (255, 255, 255)
            pixels[3] = (255, 255, 255)
            pixels[4] = (255, 255, 255)
        elif converted_view <= goal/100*60:
            print("tussen 50-60%")
            pixels[0] = (255, 255, 255)
            pixels[1] = (255, 255, 255)
            pixels[2] = (255, 255, 255)
            pixels[3] = (255, 255, 255)
            pixels[4] = (255, 255, 255)
            pixels[5] = (255, 255, 255)
        elif converted_view <= goal/100*70:
            print("tussen 60-70%")
            pixels[0] = (255, 255, 255)
            pixels[1] = (255, 255, 255)
            pixels[2] = (255, 255, 255)
            pixels[3] = (255, 255, 255)
            pixels[4] = (255, 255, 255)
            pixels[5] = (255, 255, 255)
            pixels[6] = (255, 255, 255)
        elif converted_view <= goal/100*80:
            print("tussen 70-80%")
            pixels[0] = (255, 255, 255)
            pixels[1] = (255, 255, 255)
            pixels[2] = (255, 255, 255)
            pixels[3] = (255, 255, 255)
            pixels[4] = (255, 255, 255)
            pixels[5] = (255, 255, 255)
            pixels[6] = (255, 255, 255)
            pixels[7] = (255, 255, 255)
        elif converted_view <= goal/100*90:
            print("tussen 80-90%")
            pixels[0] = (255, 255, 255)
            pixels[1] = (255, 255, 255)
            pixels[2] = (255, 255, 255)
            pixels[3] = (255, 255, 255)
            pixels[4] = (255, 255, 255)
            pixels[5] = (255, 255, 255)
            pixels[6] = (255, 255, 255)
            pixels[7] = (255, 255, 255)
            pixels[8] = (255, 255, 255)
        elif converted_view <= goal/100*99:
            print("tussen 90-99%")
            pixels[0] = (255, 255, 255)
            pixels[1] = (255, 255, 255)
            pixels[2] = (255, 255, 255)
            pixels[3] = (255, 255, 255)
            pixels[4] = (255, 255, 255)
            pixels[5] = (255, 255, 255)
            pixels[6] = (255, 255, 255)
            pixels[7] = (255, 255, 255)
            pixels[8] = (255, 255, 255)
            pixels[9] = (255, 255, 255)
        i = 100
        while i > 0:
            i -= 1
            time.sleep(0.1)
            if button_3.is_active:
                main()


def facebook_notion():
    disp.clear()
    draw.rectangle((0,0,width,height), outline=0, fill=0)
    draw.text((x + 30, top), "Facebook", font=font, font_size=30, fill=255)
    disp.image(image)
    disp.display()
    while True:
        print("u bent nu in facebook")
        create_folder()
        read_notion_facebook(databaseId_facebook, headers_post)
        facebook_likes(token_f)
        update_notion_facebook(page_id_facebook, headers_patch)
        if fb_likes_2 == fb_goal:
            print("goal reached")
            pixels.fill((255, 255, 255))
        elif fb_likes_2 <= fb_goal/100*10:
            print("tussen 0-10%")
            pixels[0] = (255, 255, 255)
        elif fb_likes_2 <= fb_goal/100*20:
            print("tussen 10-20%")
            pixels[0] = (255, 255, 255)
            pixels[1] = (255, 255, 255)
        elif fb_likes_2 <= fb_goal/100*30:
            print("tussen 20-30%")
            pixels[0] = (255, 255, 255)
            pixels[1] = (255, 255, 255)
            pixels[2] = (255, 255, 255)
        elif fb_likes_2 <= fb_goal/100*40:
            print("tussen 30-40%")
            pixels[0] = (255, 255, 255)
            pixels[1] = (255, 255, 255)
            pixels[2] = (255, 255, 255)
            pixels[3] = (255, 255, 255)
        elif fb_likes_2 <= fb_goal/100*50:
            print("tussen 40-50%")
            pixels[0] = (255, 255, 255)
            pixels[1] = (255, 255, 255)
            pixels[2] = (255, 255, 255)
            pixels[3] = (255, 255, 255)
            pixels[4] = (255, 255, 255)
        elif fb_likes_2 <= fb_goal/100*60:
            print("tussen 50-60%")
            pixels[0] = (255, 255, 255)
            pixels[1] = (255, 255, 255)
            pixels[2] = (255, 255, 255)
            pixels[3] = (255, 255, 255)
            pixels[4] = (255, 255, 255)
            pixels[5] = (255, 255, 255)
        elif fb_likes_2 <= fb_goal/100*70:
            print("tussen 60-70%")
            pixels[0] = (255, 255, 255)
            pixels[1] = (255, 255, 255)
            pixels[2] = (255, 255, 255)
            pixels[3] = (255, 255, 255)
            pixels[4] = (255, 255, 255)
            pixels[5] = (255, 255, 255)
            pixels[6] = (255, 255, 255)
        elif fb_likes_2 <= fb_goal/100*80:
            print("tussen 70-80%")
            pixels[0] = (255, 255, 255)
            pixels[1] = (255, 255, 255)
            pixels[2] = (255, 255, 255)
            pixels[3] = (255, 255, 255)
            pixels[4] = (255, 255, 255)
            pixels[5] = (255, 255, 255)
            pixels[6] = (255, 255, 255)
            pixels[7] = (255, 255, 255)
        elif fb_likes_2 <= fb_goal/100*90:
            print("tussen 80-90%")
            pixels[0] = (255, 255, 255)
            pixels[1] = (255, 255, 255)
            pixels[2] = (255, 255, 255)
            pixels[3] = (255, 255, 255)
            pixels[4] = (255, 255, 255)
            pixels[5] = (255, 255, 255)
            pixels[6] = (255, 255, 255)
            pixels[7] = (255, 255, 255)
            pixels[8] = (255, 255, 255)
        elif fb_likes_2 <= fb_goal/100*99:
            print("tussen 90-99%")
            pixels[0] = (255, 255, 255)
            pixels[1] = (255, 255, 255)
            pixels[2] = (255, 255, 255)
            pixels[3] = (255, 255, 255)
            pixels[4] = (255, 255, 255)
            pixels[5] = (255, 255, 255)
            pixels[6] = (255, 255, 255)
            pixels[7] = (255, 255, 255)
            pixels[8] = (255, 255, 255)
            pixels[9] = (255, 255, 255)
        i = 100
        while i > 0:
            i -= 1
            time.sleep(0.1)
            if button_3.is_active:
                main()


def main():
    disp.clear()
    pixels.fill((0, 0, 0))
    draw.rectangle((0,0,width,height), outline=0, fill=0)
    draw.text((x + 30, top), "Main menu", font=font, fill=255)
    disp.image(image)
    disp.display()
    print("u bent in main")
    while True:
        if button_1.is_active:
            youtube_notion()
        elif button_2.is_active:
            facebook_notion()


if __name__ == '__main__':  # code to execute if called from command-line
    main()

