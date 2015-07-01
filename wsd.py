#-*- coding: utf-8 -*-
import json
import traceback
import random
from app import *
from setting import *
from testcnn import testcnn
from crfpredict import crfpredict

corpusdb = db.corpus
dictdb = db.dict

segdict = json.loads(open('phrases.txt', 'rb').read())

@app.route('/seg', methods=['GET', 'POST'])
def seg():
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

@app.route('/wsd/<jsondata>', methods=['GET', 'POST'])
def sensedistribute(jsondata):
    data = json.loads(jsondata)
    username = data['username']
    data = data['sentence']
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
    cnnpredictlist = testcnn(data)
    crfpredictlist = crfpredict(data)
    for i in range(0, len(data)):
        if wsdata.wordlist.has_key(data[i]):
            #print wsdata.wordlist[data[i]]
            if not dbsentence:
                sentence.append({'word':data[i],'sense':wsdata.wordlist[data[i]],'predictsense':'','cnnpredictsense':cnnpredictlist[i],'crfpredictsense':crfpredictlist[i]})
            else:
                if len(dbsentence['senses'][i]) > 0 and dbsentence['senses'][i] != '[]':
                    print data[i], dbsentence['senses'][i]
                    predictsense = ''
                    tagnum = 0
                    tagged = False
                    usertag = ''
                    for sense in dbsentence['senses'][i]:
                        if 'dict' in sense['tagger']:
                            predictsense = sense['sense']
                            tagnum = 10000
                        elif len(sense['tagger']) > tagnum:
                            predictsense = sense['sense']
                            tagnum = len(sense['tagger'])
                        if not username == '':
                            if username in sense['tagger']:
                                tagged = True
                                usertag = sense['sense']
                    #print tagged
                    if tagged:
                        sentence.append({'word':data[i],'sense':wsdata.wordlist[data[i]],'predictsense':predictsense, 'tagged':1, 'usertag':usertag,'cnnpredictsense':cnnpredictlist[i],'crfpredictsense':crfpredictlist[i]})
                    else:
                        sentence.append({'word':data[i],'sense':wsdata.wordlist[data[i]],'predictsense':predictsense,'cnnpredictsense':cnnpredictlist[i],'crfpredictsense':crfpredictlist[i]})
                    print dbsentence['senses'][i][0]['sense']
                else:
                    sentence.append({'word':data[i],'sense':wsdata.wordlist[data[i]],'predictsense':'','cnnpredictsense':cnnpredictlist[i],'crfpredictsense':crfpredictlist[i]})
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
    if not tmpuser:
        result['message'] = u'请先登录'
        return json.dumps(result)  
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
            if not savelog(data['tagger'], 'addsentence', data['token'], data['sentence'], data['word'],data['sense']):
                return u'后台错误'
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
            if data['tagger'] in sense['tagger']:
                print data['tagger'], sense['tagger']
                tagged = True
                sense['tagger'].remove(data['tagger'])
            if sense['sense'] == data['sense']:
                found = True
                sense['tagger'].append(data['tagger'])
        if not found:
            dbsentence['senses'][data['word']].append({'sense':data['sense'],'tagger':[data['tagger']]})
        try:
            if tagged:
                if not savelog(data['tagger'], 'modifytag', data['token'], data['sentence'], data['word'],data['sense']):
                    return u'后台错误'
            else:
                if not savelog(data['tagger'], 'addtag', data['token'], data['sentence'], data['word'],data['sense']):
                    return u'后台错误'
            corpusdb.update_one({'sentence': dbsentence['sentence']}, {'$set':{'senses': dbsentence['senses']}})
            if tagged:
                result['message'] = u'修改标注成功'
            else:
                result['message'] = u'标注成功'
                userdb.update_one({'username':data['tagger']}, {'$inc': {'tagnum' : 1}})
            result['success'] = 1
            return json.dumps(result)
        except:
            traceback.print_exc()
            result['message'] = u'后台错误'
            return json.dumps(result)

@app.route('/addsense/<jsondata>', methods=['GET', 'POST'])
def addsense(jsondata):
    print jsondata
    data = json.loads(jsondata)
    result = {'success': 0}
    tmpuser = {}
    try:
        tmpuser = userdb.find_one({'username': data['username']})
        dbword = dictdb.find_one({'word': data['word']})
        if dbword:
            print dbword['word']
    except:
        traceback.print_exc()
        result['message'] = u'后台错误'
        return json.dumps(result)
    if not tmpuser:
        result['message'] = u'请先登录'
        return json.dumps(result)  
    if data['token'] != tmpuser['token']:
        result['message'] = u'登录已失效，请重新登录'
        return json.dumps(result)
    try:
        if not dbword.has_key('usersense'):
            dbword['usersense'] = []
        dbword['usersense'].append({'pos':data['pos'], 'sense':data['sense'],'username': data['username'],'pron':data['pron'], 'example':data['example']})
        if not savelog(data['username'], 'addsense', data['token'], data['example'], data['word'],data['sense']):
            return u'后台错误'
        dictdb.update_one({'word' :data['word']}, {'$set':{'usersense':dbword['usersense']}})
        result['success'] = 1
        result['message'] = u'添加成功'
        wsdata.refreshdict()
        return json.dumps(result)
    except:
        traceback.print_exc()
        result['message'] = u'后台错误'
        return json.dumps(result)

@app.route('/random', methods=['GET', 'POST'])
def randomcorpus():
    try:
        tmpsentence = corpusdb.find()
        sentencecount = tmpsentence.count()
        while True:
            randnum = random.randrange(sentencecount)
            if len(tmpsentence[randnum]['sentence']) <= length_limit:
                print tmpsentence[randnum]
                return tmpsentence[randnum]['sentence']
    except Exception, e:
        print 'db error'
        return u'后台错误'

@app.route('/randomcond/<cond>', methods=['GET', 'POST'])
def randomcorpuscond(cond):
    try:
        print cond
        tmpsentence = corpusdb.find({'source': cond})
        sentencecount = tmpsentence.count()
        while True:
            randnum = random.randrange(sentencecount)
            if len(tmpsentence[randnum]['sentence']) <= long_length_limit:
                print tmpsentence[randnum]
                return tmpsentence[randnum]['sentence']
    except Exception, e:
        traceback.print_exc()
        return u'后台错误'

@app.route('/randomsub', methods=['GET', 'POST'])
def randomcorpussub():
    try:
        tmpsentence = corpusdb.find({'sentence': {'$regex': subregex}})
        sentencecount = tmpsentence.count()
        while True:
            randnum = random.randrange(sentencecount)
            if len(tmpsentence[randnum]['sentence']) <= length_limit:
                print tmpsentence[randnum]
                return tmpsentence[randnum]['sentence']
    except Exception, e:
        traceback.print_exc()
        return u'后台错误'

@app.route('/randomsubcond/<cond>', methods=['GET', 'POST'])
def randomcorpussubcond(cond):
    try:
        tmpsentence = corpusdb.find({'sentence': {'$regex': subregex},'source':cond})
        sentencecount = tmpsentence.count()
        while True:
            randnum = random.randrange(sentencecount)
            if len(tmpsentence[randnum]['sentence']) <= long_length_limit:
                print tmpsentence[randnum]
                return tmpsentence[randnum]['sentence']
    except Exception, e:
        traceback.print_exc()
        return u'后台错误'