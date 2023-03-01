from flask import Flask
from threading import Thread

app = Flask('pypke-bot')

@app.route('/')
def home():
    return "The bot has successfully connected!"

def run():
  app.run(host='0.0.0.0',port=8080)

def keep_alive():  
    t = Thread(target=run)
    t.start()