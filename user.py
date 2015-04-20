#-*- coding: utf-8 -*-
import json
import datetime
import traceback
from app import *

userdb = db.user

@app.route('/register/<jsondata>', methods=['GET', 'POST'])
def register(jsondata):
    print jsondata
    data = json.loads(jsondata)
    #db
    try:
        #same username
        tmp = userdb.find_one({"username": data["username"]})
        if tmp:
            return 'username exists'
        else:
            user_id = userdb.insert_one(data).inserted_id
            print user

            return 'success'
    except:
        traceback.print_exc()
        return 'dberror'

@app.route('/login/<jsondata>', methods=['GET', 'POST'])
def login(jsondata):
    data = json.loads(jsondata)
    result = {'success': 0}
    #db
    try:
        tmp = userdb.find_one({"username": data["username"]})
        if not tmp:
            result['message'] = 'user not exists'
            return json.dumps(result)
        else:
            if tmp['password'] == data['password']:
                result['success'] = 1
                result['userid'] = str(tmp['_id'])
                result['username'] = tmp['username']
                return json.dumps(result)
            else:
                result['message'] = 'wrong password'
                return json.dumps(result)
    except:
        traceback.print_exc()
        result['message'] = 'database error'
        return json.dumps(result)

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

