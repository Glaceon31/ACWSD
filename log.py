#-*- coding: utf-8 -*-
import json
import datetime
from app import *

logdb = db.log

def savelog(username, actiontype, token, sentence = '', word = '', sense = '', message = ''):
    logdata = {}
    logdata['username'] = username
    logdata['actiontype'] = actiontype
    logdata['time'] = datetime.datetime.now()
    logdata['token'] = token
    logdata['sentence'] = sentence
    logdata['word'] = word
    logdata['sense'] = sense
    logdata['message'] = message
    #db
    try:
        logdb.insert_one(logdata)
        return 1
    except:
        traceback.print_exc()
        return 0
    #
    
