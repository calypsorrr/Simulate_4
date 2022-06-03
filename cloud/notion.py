#!/usr/bin/env python

import requests
import urllib.request
import json
import sqlite3
import time
import mysql.connector
from mysql.connector import errorcode

path = '/home/goal/webhook/token.db'

x = "'"
used_1 = "1"

config = {
  'host':'goalgetter.mysql.database.azure.com',
  'user':'goal',
  'password':'KdGaBhg4?7643',
  'database':'access_key',
  'client_flags': [mysql.connector.ClientFlag.SSL],
  'ssl_ca': 'cert/DigiCertGlobalRootG2.crt.pem'
}

def bob():
    global access_token
    conn = sqlite3.connect(path)
    c = conn.cursor()
    c.execute("SELECT used FROM notion_full ORDER BY ROWID DESC LIMIT 1")
    nummer_res = c.fetchall()
    num_1 = nummer_res[0]
    if num_1 ==(1,):
        time.sleep(10)
        bob()
    else:
        c.execute("SELECT token_notion FROM notion_full WHERE used = 0 ORDER BY ROWID DESC LIMIT 1")
        results = c.fetchall()
        token_1 = results[0]
        access_token = ''.join(token_1)
        c.execute("UPDATE notion_full SET used = " + used_1 + " WHERE token_notion = (" + x + access_token + x + ");")
        conn.commit()


def something():
    headers_1 = {
        "Authorization": "Basic MThiNWMzNGItNTBkMS00ODJmLTkzODUtMjkxY2FmOTI0ZDRjOnNlY3JldF9mT21SRllyNk11NmNEYWlLbkxVNUw0N3ZEcjF3QXNvcVJzOFcwRnU3UWdQ",
        "Content-Type": "application/json"
    }

    data = {
        "grant_type": "authorization_code",
        "code": access_token,
        "redirect_uri": "https://bo.iot.reinenbergh.com/webhook"
    }
    readUrl = "https://api.notion.com/v1/oauth/token"
    res = requests.request("POST", readUrl, headers=headers_1, json=data)
    js = res.json()
    access_1 = js["access_token"]
    email = js["owner"]["user"]["person"]["email"]
    try:
        conn = mysql.connector.connect(**config)
        print("Connection established")
    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            print("Something is wrong with the user name or password")
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
            print("Database does not exist")
        else:
            print(err)
    else:
        cursor = conn.cursor()

    cursor.execute("INSERT INTO key_access(notion_access_key, email) VALUES (%s, %s);", (access_1, email))
    print("Inserted",cursor.rowcount,"row(s) of data.")
    conn.commit()
    cursor.close()
    conn.close()
    print("Done")

def main():
    while True:
        bob()
        something()

if __name__ == '__main__':  # code to execute if called from command-line
    main()
