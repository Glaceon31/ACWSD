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

segdict = {}

@app.route('/seg', methods=['GET', 'POST'])
def mainpage():
    return render_template('seg.html')

@app.route('/wordseg/<text>', methods=['GET', 'POST'])
def wordseg(text):
    pos = 0
    nextpos = 1
    #text = text[:3]+'1'+text[3:]

    while pos < len(text)-1:
        print pos,nextpos,text,text[pos]
        if not segdict.has_key(text[pos]):
            text = text[:pos+1]+'/'+text[pos+1:]
            pos += 2
            nextpos = pos+1
            continue
        dictpos = segdict[text[pos]]
        while nextpos < len(text):
            if not dictpos.has_key(text[nextpos]):
                if nextpos >= len(text)-1:
                    break
                text = text[:nextpos]+'/'+text[nextpos:]
                pos = nextpos+1
                nextpos = pos+1
                break
            else:
                dictpos = dictpos[text[nextpos]]
            nextpos += 1

    return text

if __name__ == '__main__':
    segdict = json.loads(open('phrases.txt', 'rb').read())
    app.run('0.0.0.0', port = 6789)
