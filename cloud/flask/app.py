
from flask import Flask, request, render_template
import sqlite3

app = Flask(__name__)

path= '/home/goal/webhook/token.db'

@app.route('/')
def my_form():
    return render_template('index.html')


@app.route('/webhook', methods = ['GET'])
def my_form_post():
    x = "'"
    used="0"
    if request.method == 'GET':
        token = request.args.get('code','')
        token_2 = token.strip("")
        conn = sqlite3.connect(path)
        c = conn.cursor()
        c.execute("INSERT INTO notion_full(token_notion,used) values(" + x + token_2 + x + "," + used + ")")
        conn.commit()
    return "webhook received"

app.run(host="0.0.0.0", port=5000, debug=True)
