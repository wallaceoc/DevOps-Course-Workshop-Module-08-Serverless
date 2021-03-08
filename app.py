from flask import Flask
from time import sleep
import datetime


app = Flask(__name__)


@app.route("/")
def day():
    sleep(2)
    return "Today is " + datetime.datetime.now().strftime("%A")
