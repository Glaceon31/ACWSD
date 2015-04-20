#-*- coding: utf-8 -*-
from flask import Flask, render_template
import json
import os
import wsdata

app = Flask(__name__)
app.debug = True

cfile = open(u'corpus//corpus.txt','rb')
global corpus
corpus = json.loads(cfile.read())
cfile.close()

from pymongo import MongoClient
client = MongoClient()

db = client.wsd

from user import *
from wsd import *
from mainpage import *

if __name__ == '__main__':
    app.run('0.0.0.0')
    
