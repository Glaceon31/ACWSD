#-*- coding: utf-8 -*-
import json
import traceback
import random
import re
from app import *
from setting import *
from testcnn import testcnn, testcnnp
from crfpredict import crfpredict
import numpy as np
import urllib

corpusdb = db.corpus
dictdb = db.dict

def addpharse(phrase, segdict):
    #print phrase
    nowpos = segdict
    for i in range(0, len(phrase)):
        if nowpos.has_key(phrase[i]):
            nowpos = nowpos[phrase[i]]
            continue
        else:
            nowpos[phrase[i]] = {}
            nowpos = nowpos[phrase[i]]
            continue

def makedict(filename):
    segdict = {}
    phrases = json.loads(open(filename, 'rb').read())
    for i in phrases:
        addpharse(i,segdict)
    return segdict

segdict = makedict('phrasetext.txt')

@app.route('/seg', methods=['GET', 'POST'])
def seg():
    return render_template('seg.html')

def wordseg(text, segdict):
    result = []
    pos = 0
    nextpos = 1
    #text = text[:3]+'1'+text[3:]

    while pos < len(text):
        #print pos,nextpos,len(text),result,text[pos]
        if not segdict.has_key(text[pos]):
            result.append(text[pos:nextpos])
            pos = nextpos
            nextpos = pos+1
            continue
        dictpos = segdict[text[pos]]
        while nextpos <= len(text):
            if nextpos >= len(text):
                result.append(text[pos:nextpos])
                pos = nextpos
                nextpos = pos+1
                break
            if not dictpos.has_key(text[nextpos]):
                result.append(text[pos:nextpos])
                pos = nextpos
                nextpos = pos+1
                break
            else:
                dictpos = dictpos[text[nextpos]]
            nextpos += 1
    return result

@app.route('/wordseg/<text>', methods=['GET', 'POST'])
def wordseg2(text):
    result = wordseg(text, segdict)
    showresult = result[0]
    for i in result[1:]:
        showresult += ' '+i
    return showresult

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

@app.route('/exam', methods=['GET', 'POST'])
def exam():
    return render_template('exam.html')

def get_keyword(stem):
    kre = re.compile('<point>(.*?)</point>')
    result = kre.findall(stem)
    if len(result) >= 0:
        return result[0]
    else:
        return '' 

@app.route('/solve/<jsondata>', methods=['GET', 'POST'])
def solve(jsondata):
    jsondata = urllib.unquote(jsondata)
    jsondata = jsondata.replace('nya', '/')
    print jsondata
    result = {'success':0, 'error':u'无法解题'}
    data ={}
    #parse xml
    try:
        rehead = re.compile('<headtext>(.*?)</headtext>')
        if len(rehead.findall(jsondata)) > 0:
            data['stem'] = rehead.findall(jsondata)[0]
            retext = re.compile('<text.*?>(.*?)</text>')
            data['substem'] = retext.findall(jsondata)[0]
        else:
            retext = re.compile('<text.*?>(.*?)</text>')
            data['stem'] = retext.findall(jsondata)[0]
        for i in range(1,5):
            #print '<value="'+chr(64+i)+'">(.*?)</option>'
            reselect = re.compile('value="'+chr(64+i)+'">([\s\S]*?)</option>')
            select = reselect.findall(jsondata)[0]
            reselecttext = re.compile('\S+')
            selecttext = reselecttext.findall(select)
            data['select'+str(i)] = selecttext[0]
            result['select'+str(i)] = selecttext[0]
            if len(selecttext) == 2:
                data['subselect'+str(i)] = selecttext[1]
                result['subselect'+str(i)] = selecttext[1]
    except:
        print data
        print traceback.print_exc()
        result['error'] = u'XML格式错误'
        return json.dumps(result)
    #choose meaning of key word
    print data
    try:
        if u'加点词语' in data['stem']:
            result['type'] = 'taggingjudge'
            #choose wrong
            if u'不正确' in data['stem']:
                result['same'] = 0
                if sense1 == sense2:
                    result['pair'+str(i)] = 1
                else:
                    result['pair'+str(i)] = 0
        elif u'解释' in data['stem']:
            result['type'] = 'tagging'
            #choose right
            keyword = get_keyword(data['substem'])
            result['keyword'] = keyword
            sentence = data['substem'].replace('<point>','').replace('</point>','')
            result['sentence'] = sentence
            cnnpredictlist = testcnn(sentence)
            sense = cnnpredictlist[sentence.index(keyword)]
            result['sense'] = sense
            result['success'] = 1
        #choose word-sense pair
        #compare meaning of key word in 2 sentences
        elif u'组句' in data['stem'] or u'组语句' in data['stem']:
            result['type'] = 'sentence_pair'
            for i in range(1,5):
                keyword = get_keyword(data['select'+str(i)])
                sentencepair = data['select'+str(i)].replace('<point>','').replace('</point>','').split('$$')
                sentence1 = sentencepair[0]
                sentence2 = sentencepair[1]
                result['keyword'+str(i)] = keyword
                cnnpredictlist1 = testcnn(sentence1)
                cnnpredictlist2 = testcnn(sentence2)
                cnnp1 = testcnnp(sentence1)
                cnnp2 = testcnnp(sentence2)
                #print cnnp1
                #print cnnp2
                sense1 = cnnpredictlist1[sentence1.index(keyword)]
                p1 = cnnp1[sentence1.index(keyword)]
                result['sense'+str(i)+'_1'] = sense1
                sense2 = cnnpredictlist2[sentence2.index(keyword)]
                p2 = cnnp2[sentence2.index(keyword)]
                result['sense'+str(i)+'_2'] = sense2
                print p1
                print p2
                result['sim'+str(i)] = np.dot(p1, p2)
            #choose correct
            if u'相同' in data['stem']:
                result['same'] = 1
                if sense1 == sense2:
                    result['pair'+str(i)] = 1
                else:
                    result['pair'+str(i)] = 0
            else:
                result['same'] = 0
                if sense1 == sense2:
                    result['pair'+str(i)] = 0
                else:
                    result['pair'+str(i)] = 1
            result['success'] = 1
    except:
        print result
        print traceback.print_exc()
        return json.dumps(result)
    print result
    return json.dumps(result)

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