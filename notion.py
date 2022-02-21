import requests
import urllib.request
import RPi.GPIO as GPIO
import json
import facebook
from urllib.parse import urlparse
import time

# variabelen led's,
red = 16
orange = 20
green = 21

# variablen facebook
token_f = "EABEmtsJaaWQBAOsZBZBUSFqlU4vQUhJGGY0OlbRIt1ZCck0E2vfxJRNeKWlU50ollDwid8RTJrqvifCJPJUIJVAuSCJlnwBWqeuTodZB0Cx2JsWSvLSo1RWz7gpyRdkTpCES5tsa7RDeEM2iI0ouOjBsBNAKZCDllG7fOpeUiKo45sqRzfYmiZBOr8E9dhx1vNthLAs0Ub0wZDZD"

# variabelen youtube
token = "AIzaSyCx8-hcIQdf7taEdK_IQ03MrY1EMfrayi0"

# variablen notion
databaseId = "6b39371e9c064911a1167b02e84c3b6a"
pageid_youtube = "81fe8352-92e4-45e6-a70c-8b30b8916659"
pageid_facebook = "0a189208-2cc6-496c-a4da-2d85b98f618e"

headers_post = {
    "Accept": "application/json",
    "Notion-Version": "2021-08-16",
    "Authorization": "Bearer secret_wzb2F3FIuFZWbqgTz5ppApmG7wm0nD5A6spmeAs7a0P"
}

headers_patch = {
    "Accept": "application/json",
    "Notion-Version": "2021-08-16",
    "Content-Type": "application/json",
    "Authorization": "Bearer secret_wzb2F3FIuFZWbqgTz5ppApmG7wm0nD5A6spmeAs7a0P"
}


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


def facebook_likes(token_f):
    graph = facebook.GraphAPI(token_f)
    fields = ["new_like_count"]
    profile = graph.get_object(id_facebook, fields=fields)
    y = json.dumps(profile)
    x = json.loads(y)
    global fb_likes_2
    fb_likes_2 = (x["new_like_count"])


def youtube_id():
    global data_url
    url_data = urlparse(url_youtube)
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


def read_notion(databaseId, headers_post):
    readUrl = f"https://api.notion.com/v1/databases/{databaseId}/query"

    res = requests.request("POST", readUrl, headers=headers_post)
    data = res.json()
    global views_youtube
    global youtube_goal
    global url_youtube
    global facebook_goal
    global facebook_notion_likes
    global id_facebook
    views_youtube = data["results"][0]["properties"]["view + likes"]["number"]
    youtube_goal = data["results"][0]["properties"]["Goal"]["number"]
    url_youtube = data["results"][0]["properties"]["URL + ID"]["title"][0]["text"]["content"]
    facebook_goal = data["results"][2]["properties"]["Goal"]["number"]
    facebook_notion_likes = data["results"][2]["properties"]["view + likes"]["number"]
    id_facebook = data["results"][2]["properties"]["URL + ID"]["title"][0]["text"]["content"]

    with open('./notion.json', 'w', encoding='utf8') as f:
        json.dump(data, f, ensure_ascii=False)
    with open('./View_notion.json', 'w', encoding='utf8') as f:
        json.dump(views_youtube, f, ensure_ascii=False)
    with open('./goal_youtube_notion.json', 'w', encoding='utf8') as f:
        json.dump(youtube_goal, f, ensure_ascii=False)
    with open('./likes_notion.json', 'w', encoding='utf8') as f:
        json.dump(facebook_notion_likes, f, ensure_ascii=False)
    with open('./goal_facebook_notion.json', 'w', encoding='utf8') as f:
        json.dump(facebook_goal, f, ensure_ascii=False)
    with open('./url_youtube_notion.json', 'w', encoding='utf8') as f:
        json.dump(url_youtube, f, ensure_ascii=False)
    with open('./id_facebook_notion.json', 'w', encoding='utf8') as f:
        json.dump(id_facebook, f, ensure_ascii=False)


def update_notion_youtube(patchid_youtube, headers_patch):
    url = f"https://api.notion.com/v1/pages/{patchid_youtube}"

    updateData = {
        "properties": {
            "view + likes": {
                "id": "%3B%5Ed%40",
                "type": "number",
                "number": converted_view
            }
        }
    }

    data = json.dumps(updateData)
    response = requests.request("PATCH", url, headers=headers_patch, data=data)
    print(response.text)


def update_notion_facebook(pageid_facebook, headers_patch):
    url = f"https://api.notion.com/v1/pages/{pageid_facebook}"

    updateData = {
        "properties": {
            "view + likes": {
                "id": "%3B%5Ed%40",
                "type": "number",
                "number": fb_likes_2
            }
        }
    }
    data = json.dumps(updateData)
    response = requests.request("PATCH", url, headers=headers_patch, data=data)
    print(response.text)



def youtube():
    read_notion(databaseId, headers_post)
    youtube_id()
    read_Youtube_video(data_url, token)
    update_notion_youtube(pageid_youtube, headers_patch)
    if converted_view == youtube_goal:
        print("goal reached")
    elif converted_view <= youtube_goal/100*20:
        print("tussen 0-20%")
    elif converted_view <= youtube_goal/100*40:
        print("tussen 20-40%")
    elif converted_view <= youtube_goal/100*60:
        print("tussen 40-60%")
        orange_led(GPIO.HIGH)
        red_led(GPIO.LOW)
        green_led(GPIO.LOW)
    elif converted_view <= youtube_goal/100*80:
        print("tussen 60-80%")
    elif converted_view <= youtube_goal/100*99:
        print("tussen 80-100%")


def notion_facebook():
    read_notion(databaseId, headers_post)
    facebook_likes(token_f)
    update_notion_facebook(pageid_facebook, headers_patch)
    read_notion(databaseId, headers_post)
    if fb_likes_2 == facebook_goal:
        print("goal reached")
    elif fb_likes_2 <= facebook_goal/100*20:
        print("tussen 0-20%")
        red_led(GPIO.HIGH)
        green_led(GPIO.LOW)
    elif fb_likes_2 <= facebook_goal/100*40:
        print("tussen 20-40%")
    elif fb_likes_2 <= facebook_goal/100*60:
        print("tussen 40-60%")
    elif fb_likes_2 <= facebook_goal/100*80:
        print("tussen 60-80%")
    elif fb_likes_2 <= facebook_goal/100*99:
        print("tussen 80-100%")


def main():
    while True:
        youtube()
        print("u gaat nu naar fb")
        notion_facebook()
        time.sleep(60)


if __name__ == '__main__':  # code to execute if called from command-line
    main()