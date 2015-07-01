#-*- coding: utf-8 -*-
from flask import Flask, render_template
import json
import os
import wsdata

app = Flask(__name__)
app.debug = True

from pymongo import MongoClient
client = MongoClient()

db = client.wsd

from user import *
from wsd import *
from mainpage import *
from datafetch import load_data_word



if __name__ == '__main__':
    app.run('0.0.0.0', port = 6789)
