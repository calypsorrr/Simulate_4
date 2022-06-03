#!/usr/bin/env python
from flask import Flask, request, render_template
import csv
import io
import sys
import shutil
import time
import sqlite3
import Adafruit_GPIO.SPI as SPI
import Adafruit_SSD1306
from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont
import neopixel
import socket

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

path = '/home/pi/project_sim/fb.db'

app = Flask(__name__)

def write_file(text1, text2, text3, text4, text5, text6):

    x = '"'
    database_youtube = "youtube"
    database_facebook = "facebook"

    with open('wpa_supplicant.conf', 'a') as f:
        f.write("country=BE" + '\n' + "ctrl_interface=DIR=/var/run/wpa_supplicant GROUP=netdev" + '\n' + "update_config=1"
                + '\n' + '\n' + "network={" + '\n' + 'ssid=' + x + text1 + x + '\n' + "scan_ssid=1" + '\n' +
                'psk=' + x + text2 + x + '\n' + "key_mgmt=WPA-PSK" + '\n' + "}")

    conn = sqlite3.connect(path)
    c = conn.cursor()
    c.execute("INSERT INTO dhtreadings(fbid) values("+ x + text3 + x + ")")
    conn.commit()
    c.execute("INSERT INTO notion(id, database_id) values("+ x + database_youtube + x + "," + x + text4 + x + ")")
    conn.commit()
    c.execute("INSERT INTO notion(id, database_id) values("+ x + database_facebook + x + "," + x + text5 + x + ")")
    conn.commit()
    c.execute("INSERT INTO email_notion(email) values("+ x + text6 + x + ")")
    conn.commit()
    conn.close()

    original = '/home/pi/wpa_supplicant.conf'
    target = '/home/pi/project_sim/bob'
    shutil.move(original, target)

def shutdown_server():
    func = request.environ.get('werkzeug.server.shutdown')
    if func is None:
        raise RuntimeError('Not running with the Werkzeug Server')
    func()


@app.route('/shutdown', methods=['POST'])
def shutdown():
    shutdown_server()
    return 'Server shutting down...'

@app.route('/')
def my_form():
    return render_template('index.html')

@app.route('/', methods = ['POST'])
def my_form_post():
    if request.method == 'POST':
        text1 = request.form['ssid']
        text2 = request.form['passwoord']
        text3 = request.form['fb']
        text4 = request.form['id_youtube']
        text5 = request.form['id_facebook']
        text6 = request.form['email_user']
        write_file(text1, text2, text3, text4, text5, text6)
        return shutdown()

def extract_ip():
    st = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        st.connect(('10.255.255.255', 1))
        IP = st.getsockname()[0]
    except Exception:
        time.sleep(5)
        extract_ip()
    finally:
        st.close()
    return IP
print(extract_ip())

if __name__ == "__main__":
    disp.clear()
    draw.rectangle((0,0,width,height), outline=0, fill=0)
    draw.text((x + 20, top), extract_ip(), font=font, fill=255)
    disp.image(image)
    disp.display()
    app.run(port=8000, host = '0.0.0.0', debug = True)
