#-*- coding: utf-8 -*-
import json

def savelog(userid, username, actiontype, datetime, sentence, sense, message):
    #db
    try:
        a = 1
    except:
        print 'dberror'
        return 0
    #
    return 1
