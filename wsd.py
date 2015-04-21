#-*- coding: utf-8 -*-
import json
import traceback
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
    global corpus
    print jsondata
    data = json.loads(jsondata)
    dbsentence = ''
    try:
        dbsentence = corpusdb.find_one({'sentence': data['sentence']})
        if dbsentence:
            print dbsentence['sentence']
    except:
        traceback.print_exc()
        print 'db error'
        dbsentence = ''   
    if not dbsentence:
        tmp = {}
        tmp['sentence'] = data['sentence']
        tmp['senses'] = []
        for i in range(0, len(data['sentence'])):
            tmp['senses'].append([])
        tmp['senses'][data['word']].append({'tagger': [data['tagger']], 'sense':data['sense']}) 
        try:
            corpusdb.insert_one(tmp)
        except:
            traceback.print_exc()
            return 'db error'
    else:
        found = False
        for sense in dbsentence['senses'][data['word']]:
            if sense['sense'] == data['sense']:
                found = True
                sense['tagger'].append(data['tagger'])
                break
        if not found:
            dbsentence['senses'][data['word']].append({'sense':data['sense'],'tagger':[data['tagger']]})
        try:
            corpusdb.update_one({'sentence': dbsentence['sentence']}, {'$set':{'senses': dbsentence['senses']}})
        except:
            traceback.print_exc()
            return 'db error'
    return '1'
