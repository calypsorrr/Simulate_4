#!/usr/bin/env python
"""
Simulate 4 project
"""

import time
import requests
import urllib.request
import RPi.GPIO as GPIO
from gpiozero import Button
import json
import facebook
from urllib.parse import urlparse
import os

__author__ = "Bo Claes"
__email__ = "bo.claes@student.kdg.be"
__status__ = "Development"

# variabelen led's, buttons
button_1 = Button(pin=18)
button_2 = Button(pin=12)

red = 16
orange = 20
green = 21

# path waar de folder gemaakt moet worden
path = "/home/pi/logs"

# variablen facebook
token_f = "EABEmtsJaaWQBADj3gyAVTZBTNThfXPLlrHcQ7PfUi3A1yY1eBAgBZC3Q2AIKkjN6ivZBpM4viWiuH6l6CFXaZA2vHAAqJlVR5dpaRmtMxCcFGszcoRjB1tYT2qlhKB223CxUedV4OZB0ZCpQKBM0W5WiEaiBrZBJgb5jtsp7F8fae98v5nCr5ZB0iTl3qeuC5Vo3H9xlveKhi0LAqQXYqZBhk"

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


def red_led(led):
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    GPIO.setup(red, GPIO.OUT)
    GPIO.output(red, led)


def green_led(led):
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    GPIO.setup(green, GPIO.OUT)
    GPIO.output(green, led)


def orange_led(led):
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    GPIO.setup(orange, GPIO.OUT)
    GPIO.output(orange, led)


def clear_led():
    red_led(GPIO.LOW)
    orange_led(GPIO.LOW)
    green_led(GPIO.LOW)

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
    with open('logs/facebook_likes.json', 'w', encoding='utf8') as f:
        json.dump(fb_likes_2, f, ensure_ascii=False)


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

    with open('logs/notion_youtube.json', 'w', encoding='utf8') as f:
        json.dump(data, f, ensure_ascii=False)


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
    while True:
        print("u bent nu in youtube")
        clear_led()
        create_folder()
        read_notion_Youtube_id(databaseId_Youtube, headers_post)
        youtube_id()
        read_Youtube_video(data_url, token)
        update_notion_youtube(page_id_youtube, headers_patch)
        if converted_view == goal:
            print("goal reached")
            red_led(GPIO.LOW)
            orange_led(GPIO.LOW)
            green_led(GPIO.HIGH)
        elif converted_view <= goal/100*20:
            print("tussen 0-20%")
            red_led(GPIO.HIGH)
            orange_led(GPIO.LOW)
            green_led(GPIO.LOW)
        elif converted_view <= goal/100*40:
            print("tussen 20-40%")
            red_led(GPIO.HIGH)
            orange_led(GPIO.LOW)
            green_led(GPIO.LOW)
        elif converted_view <= goal/100*60:
            print("tussen 40-60%")
            orange_led(GPIO.HIGH)
            red_led(GPIO.LOW)
            green_led(GPIO.LOW)
        elif converted_view <= goal/100*80:
            print("tussen 60-80%")
            orange_led(GPIO.LOW)
            green_led(GPIO.HIGH)
            red_led(GPIO.LOW)
        elif converted_view <= goal/100*99:
            print("tussen 80-100%")
            green_led(GPIO.HIGH)
            orange_led(GPIO.LOW)
            red_led(GPIO.LOW)
        i = 10
        while i > 0:
            i -= 1
            time.sleep(1)
            if button_1.is_active:
                return


def facebook_notion():
    while True:
        print("u bent nu in facebook")
        clear_led()
        create_folder()
        read_notion_facebook(databaseId_facebook, headers_post)
        facebook_likes(token_f)
        update_notion_facebook(page_id_facebook, headers_patch)
        if fb_likes_2 == fb_goal:
            print("goal reached")
            red_led(GPIO.LOW)
            orange_led(GPIO.LOW)
            green_led(GPIO.HIGH)
        elif fb_likes_2 <= fb_goal/100*20:
            print("tussen 0-20%")
            red_led(GPIO.HIGH)
            orange_led(GPIO.LOW)
            green_led(GPIO.LOW)
        elif fb_likes_2 <= fb_goal/100*40:
            print("tussen 20-40%")
            red_led(GPIO.HIGH)
            orange_led(GPIO.LOW)
            green_led(GPIO.LOW)
        elif fb_likes_2 <= fb_goal/100*60:
            print("tussen 40-60%")
            orange_led(GPIO.HIGH)
            red_led(GPIO.LOW)
            green_led(GPIO.LOW)
        elif fb_likes_2 <= fb_goal/100*80:
            print("tussen 60-80%")
            orange_led(GPIO.LOW)
            green_led(GPIO.HIGH)
            red_led(GPIO.LOW)
        elif fb_likes_2 <= fb_goal/100*99:
            print("tussen 80-100%")
            green_led(GPIO.HIGH)
            orange_led(GPIO.LOW)
            red_led(GPIO.LOW)
        i = 10
        while i > 0:
            i -= 1
            time.sleep(1)
            if button_1.is_active:
                return


def main():
    while True:
        if button_1.is_active:
            youtube_notion()
        elif button_2.is_active:
            facebook_notion()


if __name__ == '__main__':  # code to execute if called from command-line
    main()
