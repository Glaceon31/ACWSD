#-*- coding: utf-8 -*-
import json
from app import *

@app.route('/register/<jsondata>', methods=['GET', 'POST'])
def register(jsondata):
    print jsondata
    data = json.loads(jsondata)
    #db
    try:
        a = 1
    except:
        print 'dberror'
        return 'dberror'
    #
    return 'success'

@app.route('/login/<jsondata>', methods=['GET', 'POST'])
def login(jsondata):
    data = json.loads(jsondata)
    password = ''
    #db
    try:
        a = 1
    except:
        print 'dberror'
        return 0
    #
    if data['password'] != password:
        return 'wrong password'
    token = ''
    result = ''
    return result

@app.route('/logout/<jsondata>', methods=['GET', 'POST'])
def logout(jsondata):
    data = json.loads(jsondata)
    #db
    try:
        a = 1
    except:
        print 'dberror'
        return 0
    #
    return 1

@app.route('/getinfo/<jsondata>', methods=['GET', 'POST'])
def getinfo(jsondata):
    data = json.loads(jsondata)
    token= ''
    #db
    try:
        a = 1
    except:
        print 'dberror'
        return 0
    #
    if data['token'] != token:
        return 0
    result = ''
    return result

@app.route('/modify/<jsondata>', methods=['GET', 'POST'])
def modify(jsondata):
    data = json.loads(jsondata)
    token = ''
    #db
    try:
        a = 1
    except:
        print 'dberror'
        return 0
    #
    if data['token'] != token:
        return 0
    result = ''
    return result

@app.route('/modifypassword/<jsondata>', methods=['GET', 'POST'])
def modifypassword(jsondata):
    data = json.loads(jsondata)
    token = ''
    password = ''
    #db
    try:
        a = 1
    except:
        print 'dberror'
        return 0
    #
    if data['token'] != token or data['password'] != password:
        return 0
    result = ''
    return result

