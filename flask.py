#!/usr/bin/env python
from flask import Flask, request, render_template
import csv
import io
import sys
import shutil
import time

app = Flask(__name__)

def write_file(text1, text2, text3):

    x = '"'
    with open('wpa_supplicant.conf', 'a') as f:
        f.write("country=BE" + '\n' + "ctrl_interface=DIR=/var/run/wpa_supplicant GROUP=netdev" + '\n' + "update_config=1"
                + '\n' + '\n' + "network={" + '\n' + 'ssid=' + x + text1 + x + '\n' + "scan_ssid=1" + '\n' +
                'psk=' + x + text2 + x + '\n' + "key_mgmt=WPA-PSK" + '\n' + "}")
    with open('fb.txt', 'a') as f:
        f.write(x + text3 + x)

    original = '/home/pi/wpa_supplicant.conf'
    target = '/home/pi/python_flask/bob/wpa_supplicant.conf'
    shutil.move(original, target)

@app.route('/')
def my_form():
    return render_template('index.html')

@app.route('/', methods = ['GET','POST'])
def my_form_post():
    if request.method == 'POST':
        text1 = request.form['ssid']
        text2 = request.form['passwoord']
        text3 = request.form['fb']
        write_file(text1, text2, text3)
        time.sleep(10)
        sys.exit(0)
    elif request.method == "GET":
        return render_template('index.html')

if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True, port=8080)