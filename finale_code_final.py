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
import mysql.connector
from mysql.connector import errorcode


__author__ = "Bo Claes"
__email__ = "bo.claes@student.kdg.be"
__status__ = "Development"

y = '"'


# Every config for the LCD screen
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

# Led strip config
LED_COUNT = 5
pixels = neopixel.NeoPixel(board.D18,LED_COUNT)


# config for connecting to database on the cloud
config = {
  'host':'goalgetter.mysql.database.azure.com',
  'user':'goal',
  'password':'KdGaBhg4?7643',
  'database':'access_key',
  'client_flags': [mysql.connector.ClientFlag.SSL],
  'ssl_ca': '/home/pi/project_sim/cert/DigiCertGlobalRootG2.crt.pem'
}

global access_token
global databaseId_youtube_sql
global databaseId_facebook_sql
global access_key_notion

def database():
    try:
        # path to database
        path = '/home/pi/project_sim/fb.db'
        # Getting the Youtube notion id and facebook notion id from the database
        cn = sqlite3.connect(path)
        c = cn.cursor()
        c.execute("SELECT fbid FROM dhtreadings ORDER BY ROWID DESC LIMIT 1;")
        results = c.fetchall()
        id = results[0]
        access_token = ''.join(id)
        c.execute("SELECT database_id FROM notion WHERE id = 'youtube';")
        results_youtube = c.fetchall()
        id_youtube = results_youtube[0]
        databaseId_youtube_sql = ''.join(id_youtube)
        c.execute("SELECT database_id FROM notion WHERE id = 'facebook';")
        results_facebook = c.fetchall()
        id_facebook = results_facebook[0]
        databaseId_facebook_sql = ''.join(id_facebook)
        c.execute("SELECT email FROM email_notion;")
        result_email = c.fetchall()
        res_email = result_email[0]
        res_email_sql = ''.join(res_email)
        cn.close()
        print(res_email_sql)

        # connection to the database on the cloud and getting the access key
        # try:
        conn = mysql.connector.connect(**config)
        print("Connection established")
        # except mysql.connector.Error as err:
        #   if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
        #     print("Something is wrong with the user name or password")
        #   elif err.errno == errorcode.ER_BAD_DB_ERROR:
        #     print("Database does not exist")
        #   else:
        #     print(err)
        # else:
        cursor = conn.cursor()
        cursor.execute("SELECT notion_access_key FROM key_access WHERE email ="+ y + res_email_sql+ y + "LIMIT 1")
        result = cursor.fetchall()
        bob = result[0]
        access_key_notion = ''.join(bob)
        print(access_key_notion)
        rows = cursor.fetchall()
        print("Read",cursor.rowcount,"row(s) of data.")
        conn.commit()
        cursor.close()
        conn.close()
        print("Done")
    except:
        disp.clear()
        pixels.fill((0, 0, 0))
        draw.rectangle((0, 0, width, height), outline=0, fill=0)
        draw.text((x + 0, top), "ERROR WITH DATABASE", font=font, fill=255)
        disp.image(image)
        disp.display()
        database()

# Variable led's, buttons
button_1 = Button(pin=21)
button_2 = Button(pin=12)
button_3 = Button(pin=26)


# Path to where the file and folder needs to be maked
path = "/home/pi/project_sim/logs"
path_2 = "/home/pi/escape.txt"

# Variable Facebook
token_f = access_token

# Variable Youtube
token = "AIzaSyCx8-hcIQdf7taEdK_IQ03MrY1EMfrayi0"

# Variable Notion
databaseId_Youtube = databaseId_youtube_sql
databaseId_facebook = databaseId_facebook_sql

headers_patch = {
    "Accept": "application/json",
    "Notion-Version": "2021-08-16",
    "Content-Type": "application/json",
    "Authorization": "Bearer " + access_key_notion
}

headers_post = {
    "Accept": "application/json",
    "Notion-Version": "2021-08-16",
    "Authorization": "Bearer " + access_key_notion
}

# API to insert Youtube notion id
readUrl = f"https://api.notion.com/v1/databases/{databaseId_Youtube}/query"
res = requests.request("POST", readUrl, headers=headers_post)
data = res.json()
youtube_insert_id = data["results"][0]["id"]
with open('/home/pi/project_sim/logs/youtube_insert_id.json', 'w', encoding='utf8') as f:
    json.dump(data, f, ensure_ascii=False)
page_id_youtube = youtube_insert_id


# API to insert Facebook notion id
readUrl = f"https://api.notion.com/v1/databases/{databaseId_facebook}/query"
res = requests.request("POST", readUrl, headers=headers_post)
data = res.json()
fb_insert_id = data["results"][0]["id"]
with open('/home/pi/project_sim/logs/facebook_insert_id.json', 'w', encoding='utf8') as f:
    json.dump(data, f, ensure_ascii=False)
page_id_facebook = fb_insert_id

# Creating the folder logs
def create_folder():
    try:
        os.mkdir(path)
    except FileExistsError:
        print("folder already exist")

# Creating the file escape.txt
def create_escape():
    try:
        open(path_2, "x")
    except FileExistsError:
        print("file already exist")

# Getting the likes from Facebook
def facebook_likes(token_f):
    graph = facebook.GraphAPI(token_f)
    fields = ["new_like_count"]
    profile = graph.get_object(fb_id, fields=fields)
    y = json.dumps(profile)
    x = json.loads(y)
    global fb_likes_2
    fb_likes_2 = (x["new_like_count"])

    with open('/home/pi/project_sim/logs/facebook.json', 'w', encoding='utf8') as f:
        json.dump(profile, f, ensure_ascii=False)

# Getting the Youtube id out of the URL
def youtube_id():
    global data_url
    url_data = urlparse(url)
    data_url = url_data.query[2::]

    with open('/home/pi/project_sim/logs/youtube_id.json', 'w', encoding='utf8') as f:
        json.dump(data_url, f, ensure_ascii=False)

# Getting the view count out of the URL
def read_Youtube_video(data_url, token):
    data = urllib.request.urlopen(
        f"https://www.googleapis.com/youtube/v3/videos?part=statistics&id={data_url}&key={token}").read()
    viewcount = json.loads(data)["items"][0]["statistics"]["viewCount"]
    global converted_view
    converted_view = int(viewcount)

    with open('/home/pi/project_sim/logs/youtube_views.json', 'w', encoding='utf8') as f:
        json.dump(converted_view, f, ensure_ascii=False)

# API for getting the data out of notion Youtube
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
    with open('/home/pi/project_sim/logs/youtube.json', 'w', encoding='utf8') as f:
        json.dump(data, f, ensure_ascii=False)



# API for getting the data out of notion Facebook
def read_notion_facebook(databaseId_facebook, headers_post):
    readUrl = f"https://api.notion.com/v1/databases/{databaseId_facebook}/query"

    res = requests.request("POST", readUrl, headers=headers_post)
    data = res.json()
    global fb_goal
    global fb_likes
    global fb_id
    fb_goal = data["results"][0]["properties"]["Goal"]["number"]
    fb_likes = data["results"][0]["properties"]["Likes"]["number"]
    fb_id = data["results"][0]["properties"]["Facebook_id"]["title"][0]["text"]["content"]
    with open('/home/pi/project_sim/logs/read_facebook.json', 'w', encoding='utf8') as f:
        json.dump(fb_id, f, ensure_ascii=False)

# Updating the youtube notion page
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

# Updating the facebook notion page
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

# Display youtube on the LCD screen + setting the led strip up based on some % calculations
def youtube_notion():
    database()
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
            pixels.fill((50, 50, 50))
        elif converted_view <= goal/100*20:
            print("Tussen 0 en 20%")
            pixels[0] = (50, 50, 50)
        elif converted_view <= goal/100*40:
            print("Tussen 20 en 40%")
            pixels[0] = (50, 50, 50)
            pixels[1] = (50, 50, 50)
        elif converted_view <= goal/100*60:
            print("Tussen 40 en 60%")
            pixels[0] = (50, 50, 50)
            pixels[1] = (50, 50, 50)
            pixels[2] = (50, 50, 50)
        elif converted_view <= goal/100*80:
            print("Tussen 60 en 80%")
            pixels[0] = (50, 50, 50)
            pixels[1] = (50, 50, 50)
            pixels[2] = (50, 50, 50)
            pixels[3] = (50, 50, 50)
        i = 1000
        while i > 0:
            i -= 1
            time.sleep(0.1)
            if button_3.is_active:
                main()

# Display facebook on the LCD screen + setting the led strip up based on some % calculations
def facebook_notion():
    database()
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
            pixels.fill((50, 50, 50))
        elif fb_likes_2 <= fb_goal/100*20:
            print("Tussen 0 en 20%")
            pixels[0] = (50, 50, 50)
        elif fb_likes_2 <= fb_goal/100*40:
            print("Tussen 20 en 40%")
            pixels[0] = (50, 50, 50)
            pixels[1] = (50, 50, 50)
        elif fb_likes_2 <= fb_goal/100*60:
            print("Tussen 40 en 60%")
            pixels[0] = (50, 50, 50)
            pixels[1] = (50, 50, 50)
            pixels[2] = (50, 50, 50)
        elif fb_likes_2 <= fb_goal/100*80:
            print("Tussen 60 en 80%")
            pixels[0] = (50, 50, 50)
            pixels[1] = (50, 50, 50)
            pixels[2] = (50, 50, 50)
            pixels[3] = (50, 50, 50)
        i = 1000
        while i > 0:
            i -= 1
            time.sleep(0.1)
            if button_3.is_active:
                main()

# Display Main menu on the lcd screen + setting everything in a main loop
def main():
    try:
        database()
        create_escape()
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
    except:
        disp.clear()
        pixels.fill((0, 0, 0))
        draw.rectangle((0,0,width,height), outline=0, fill=0)
        draw.text((x + 30, top), "ERROR", font=font, fill=255)
        disp.image(image)
        disp.display()


if __name__ == '__main__':  # code to execute if called from command-line
    main()
