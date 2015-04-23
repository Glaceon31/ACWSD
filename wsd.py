#-*- coding: utf-8 -*-
import json
import traceback
import random
from app import *

corpusdb = db.corpus

@app.route('/wsd/<data>', methods=['GET', 'POST'])
def sensedistribute(data):
    sentence = []
    print len(wsdata.wordlist)
    dbsentence = ''
    try:
        dbsentence = corpusdb.find_one({'sentence': {'$regex':data}})
        if dbsentence:
            print dbsentence['sentence']
    except:
        print 'db error'
        dbsentence = ''
    for i in range(0, len(data)):
        if wsdata.wordlist.has_key(data[i]):
            if not dbsentence:
                sentence.append({'word':data[i],'sense':wsdata.wordlist[data[i]],'predictsense':''})
            else:
                if len(dbsentence['senses'][i]) > 0 and dbsentence['senses'][i] != '[]':
                    print data[i], dbsentence['senses'][i]
                    sentence.append({'word':data[i],'sense':wsdata.wordlist[data[i]],'predictsense':dbsentence['senses'][i][0]['sense']})
                    print dbsentence['senses'][i][0]['sense']
                else:
                    sentence.append({'word':data[i],'sense':wsdata.wordlist[data[i]],'predictsense':''})
        else:
            sentence.append({'word':data[i],'sense':''})
    return json.dumps(sentence)

@app.route('/update/<jsondata>', methods=['GET', 'POST'])
def update(jsondata):
    print jsondata
    data = json.loads(jsondata)
    result = {'success': 0}
    dbsentence = {}
    tmpuser = {}
    try:
        tmpuser = userdb.find_one({'username': data['tagger']})
        dbsentence = corpusdb.find_one({'sentence': data['sentence']})
        if dbsentence:
            print dbsentence['sentence']
    except:
        traceback.print_exc()
        print 'db error'
        dbsentence = '' 
    if data['token'] != tmpuser['token']:
        result['message'] = u'登录已失效，请重新登录'
        return json.dumps(result)  
    if not dbsentence:
        tmp = {}
        tmp['sentence'] = data['sentence']
        tmp['senses'] = []
        tmp['adder'] = data['tagger']
        for i in range(0, len(data['sentence'])):
            tmp['senses'].append([])
        tmp['senses'][data['word']].append({'tagger': [data['tagger']], 'sense':data['sense']}) 
        try:
            corpusdb.insert_one(tmp)
            result['message'] = u'标注成功'
            result['success'] = 1
            return json.dumps(result)
        except:
            traceback.print_exc()
            result['message'] = u'后台错误'
            return json.dumps(result)
    else:
        found = False
        tagged = False
        for sense in dbsentence['senses'][data['word']]:
            if not isinstance(sense, dict):
                dbsentence['senses'][data['word']] = []
                continue
            if sense['sense'] == data['sense']:
                found = True
                sense['tagger'].append(data['tagger'])
            if data['tagger'] in sense['tagger']:
                tagged = True
                sense['tagger'].remove(data['tagger'])
        if not found:
            dbsentence['senses'][data['word']].append({'sense':data['sense'],'tagger':[data['tagger']]})
        try:
            corpusdb.update_one({'sentence': dbsentence['sentence']}, {'$set':{'senses': dbsentence['senses']}})
            if tagged:
                result['message'] = u'修改标注成功'
            else:
                result['message'] = u'标注成功'
            result['success'] = 1
            return json.dumps(result)
        except:
            traceback.print_exc()
            result['message'] = u'后台错误'
            return json.dumps(result)

@app.route('/random', methods=['GET', 'POST'])
def randomcorpus():
    try:
        sentencecount = corpusdb.count()
        randnum = random.randrange(sentencecount)
        tmpsentence = corpusdb.find()
        print tmpsentence[randnum]
        return tmpsentence[randnum]['sentence']
    except Exception, e:
        print 'db error'
        return u'后台错误'