#-*- coding: utf-8 -*-
import json
import datetime
import traceback
import random
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
            return u'用户名已存在'
        else:
            user_id = userdb.insert_one(data).inserted_id
            print user_id
            return u'注册成功'
    except:
        traceback.print_exc()
        return u'后台错误'

@app.route('/login/<jsondata>', methods=['GET', 'POST'])
def login(jsondata):
    data = json.loads(jsondata)
    result = {'success': 0}
    #db
    try:
        tmp = userdb.find_one({"username": data["username"]})
        if not tmp:
            result['message'] = u'用户不存在'
            return json.dumps(result)
        else:
            if tmp['password'] == data['password']:
                tokenlength = random.randrange(16,32)
                token = ''
                for i in range(0, tokenlength):
                    token += random.choice('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789')
                result['success'] = 1
                result['userid'] = str(tmp['_id'])
                result['username'] = tmp['username']
                result['name'] = tmp['name']
                result['token'] = token
                userdb.update_one({'_id': tmp['_id']}, {'$set':{'token' : token}})
                return json.dumps(result)
            else:
                result['message'] = u'密码错误'
                return json.dumps(result)
    except:
        traceback.print_exc()
        result['message'] = u'后台错误'
        return json.dumps(result)

@app.route('/logout/<jsondata>', methods=['GET', 'POST'])
def logout(jsondata):
    data = json.loads(jsondata)
    #db
    try:
        tmp = userdb.find_one({'username': data['username']})
        if tmp['token'] == data['token']:
            userdb.update_one({'username': data['username']}, {'$set':{'token' : ''}})
    except:
        traceback.print_exc()
        return '0'
    #
    return '1'

@app.route('/getinfo/<jsondata>', methods=['GET', 'POST'])
def getinfo(jsondata):
    data = json.loads(jsondata)
    result = {}
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
    result = {'success': 0 }
    #db
    try:
        tmp = userdb.find_one({'username': data['username']})
    except:
        traceback.print_exc()
        result['message'] = u'后台错误'
        return json.dumps(result)
    #
    if data['token'] != tmp['token']:
        result['message'] = u'登录已失效，请重新登录'
        return json.dumps(result)
    else:
        try:
            userdb.update_one({'username': data['username']}, {'$set':{'name' : data['name']}})
        except:
            traceback.print_exc()
            result['message'] = u'后台错误'
            return json.dumps(result)
        result['message'] = u'修改成功'
        result['success'] = 1
        return json.dumps(result)

@app.route('/modifypassword/<jsondata>', methods=['GET', 'POST'])
def modifypassword(jsondata):
    data = json.loads(jsondata)
    result = {'success':0}
    #db
    try:
        tmp = userdb.find_one({'username': data['username']})
    except:
        traceback.print_exc()
        result['message'] = u'后台错误'
        return json.dumps(result)
    #
    if data['token'] != tmp['token']:
        result['message'] = u'登录已失效，请重新登录'
        return json.dumps(result)
    elif data['oldpass'] != tmp['password']:
        result['message'] = u'原密码错误'
        return json.dumps(result)
    else:
        try:
            userdb.update_one({'username': data['username']}, {'$set':{'password' : data['newpass']}})
        except:
            traceback.print_exc()
            result['message'] = u'后台错误'
            return json.dumps(result)
        result['success'] = 1
        result['message'] = u'修改成功'
        return json.dumps(result)

