#!/usr/bin/env python
from flask import Flask, request, render_template
import csv
import io
import sys
import shutil
import time
import sqlite3

app = Flask(__name__)

def write_file(text1, text2, text3, text4, text5, text6):

    x = '"'
    database_youtube = "youtube"
    database_facebook = "facebook"

    with open('wpa_supplicant.conf', 'a') as f:
        f.write("country=BE" + '\n' + "ctrl_interface=DIR=/var/run/wpa_supplicant GROUP=netdev" + '\n' + "update_config=1"
                + '\n' + '\n' + "network={" + '\n' + 'ssid=' + x + text1 + x + '\n' + "scan_ssid=1" + '\n' +
                'psk=' + x + text2 + x + '\n' + "key_mgmt=WPA-PSK" + '\n' + "}")

    conn = sqlite3.connect('fb.db')
    c = conn.cursor()
    c.execute("INSERT INTO dhtreadings(fbid) values("+ x + text3 + x + ")")
    conn.commit()
    c.execute("INSERT INTO notion(id, database_id) values("+ x + database_youtube + x + "," + x + text4 + x + ")")
    conn.commit()
    c.execute("INSERT INTO notion(id, database_id) values("+ x + database_facebook + x + "," + x + text5 + x + ")")
    conn.commit()
    c.execute("INSERT INTO email_notion(email_notion) values"+ x + text6 + x + ")")
    conn.close()

    original = '/home/pi/project_sim/wpa_supplicant.conf'
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
        text6 = request.form['email_notion']
        write_file(text1, text2, text3, text4, text5, text6)
        return shutdown()

if __name__ == "__main__":
    app.run(port=8000, host = '0.0.0.0')
