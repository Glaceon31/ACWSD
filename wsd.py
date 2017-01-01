#-*- coding: utf-8 -*-
import json
import traceback
import random
import re
from app import *
from setting import *
from testcnn import testcnn, testcnnp, testcnn_one, testcnnp_one
from crfpredict import crfpredict
from solve import solveprocess
from solve import solve as solveweb
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


def geteditdistance(a,b):
    if len(a) == 0:
        return len(b)
    if len(b) == 0:
        return len(a)
    matrix = np.zeros((len(b)+1, len(a)+1))
    for i in xrange(len(b)+1):
        matrix[i][0] = i
    for j in xrange(len(a)+1):
        matrix[0][j] = j
    for i in range(1,len(b)+1):
        for j in range(1,len(a)+1):
            if b[i-1] == a[j-1]:
                matrix[i][j] = matrix[i-1][j-1]
            else:
                matrix[i][j] = min(matrix[i-1][j-1]+1,matrix[i][j-1]+1,matrix[i-1][j]+1)        
    return matrix[len(b)][len(a)]

def max_matching(a,b):
    if len(a) > len(b):
        tmp = a
        a = b
        b = tmp
    res = len(a)
    while res > 0:
        matched = False
        for i in xrange(len(a)-res+1):
            if b.find(a[i:i+res]) >= 0:
                matched = True
        if matched:
            break
        res = res-1
    return res

@app.route('/solve/<jsondata>', methods=['GET', 'POST'])
def solve(jsondata):
    jsondata = urllib.unquote(jsondata)
    jsondata = jsondata.replace('nya', '/')
    result = solveweb(jsondata, web=True)
    print result
    return json.dumps(result)

@app.route('/wsdinterface', methods=['POST'])
def interface():
    jsondata = request.form['xml']
    print jsondata
    result = solveprocess(jsondata)
    responsexml = jsondata
    print result
    if result['type'] == 'taggingjudge':
        print 'taggingjudge'
        if result['same'] == 1:
            mind = 100000
            ans = -1
        else:
            maxd = 0
            ans = -1
        for i in range(1,5):
            ed=geteditdistance(result['sense'+str(i)], result['judgesense'+str(i)])
            mm=max_matching(result['sense'+str(i)], result['judgesense'+str(i)])
            print result['sense'+str(i)], result['judgesense'+str(i)], ed, mm
            if result['same'] == 1:
                if ed+100-mm < mind:
                    ans = i
                    mind = ed+100-mm
            else:
                if ed+100-mm > maxd:
                    ans = i
                    maxd = ed+100-mm
    elif result['type'] == 'tagging':
        print 'tagging'
        mind = 100000
        ans = -1
        for i in range(1,5):
            ed=geteditdistance(result['sense'], result['select'+str(i)])
            mm=max_matching(result['sense'], result['select'+str(i)])
            print result['sense'], result['select'+str(i)],ed, mm
            if ed+100-mm < mind:
                ans = i
                mind = ed+100-mm
    elif result['type'] == 'sentence_pair':
        print 'sentencepair'
        ans = -1
        if result['same'] == 1:
            sim = 0
        else:
            sim = 1.
        for i in range(1,5):
            comval = result['sim'+str(i)]
            print result['sense'+str(i)+'_1'],result['sense'+str(i)+'_2'],comval
            if result['same'] == 1:
                if result['sense'+str(i)+'_1'] == result['sense'+str(i)+'_2']:
                    comval += 1.0
                if comval > sim:
                    ans = i
                    sim = comval
            else:
                if result['sense'+str(i)+'_1'] != result['sense'+str(i)+'_2']:
                    comval -= 1.0
                if comval < sim:
                    ans = i
                    sim = comval

    ansselect = ['','A','B','C','D']
    responsexml = responsexml.replace('</question>','<answer org="THU">\n           '+ansselect[ans]+'\n            </answer>\n</question>')
    return responsexml

@app.route('/wsdansinterface', methods=['POST'])
def ansinterface():
    jsondata = request.form['xml']
    print jsondata
    result = solveprocess(jsondata)
    responsexml = jsondata
    print result
    if result['type'] == 'taggingjudge':
        print 'taggingjudge'
        if result['same'] == 1:
            mind = 100000
            ans = -1
        else:
            maxd = 0
            ans = -1
        for i in range(1,5):
            ed=geteditdistance(result['sense'+str(i)], result['judgesense'+str(i)])
            mm=max_matching(result['sense'+str(i)], result['judgesense'+str(i)])
            print result['sense'+str(i)], result['judgesense'+str(i)], ed, mm
            if result['same'] == 1:
                if ed+100-mm < mind:
                    ans = i
                    mind = ed+100-mm
            else:
                if ed+100-mm > maxd:
                    ans = i
                    maxd = ed+100-mm
    elif result['type'] == 'tagging':
        print 'tagging'
        mind = 100000
        ans = -1
        for i in range(1,5):
            ed=geteditdistance(result['sense'], result['select'+str(i)])
            mm=max_matching(result['sense'], result['select'+str(i)])
            print result['sense'], result['select'+str(i)],ed, mm
            if ed+100-mm < mind:
                ans = i
                mind = ed+100-mm
    elif result['type'] == 'sentence_pair':
        print 'sentencepair'
        ans = -1
        if result['same'] == 1:
            sim = 0
        else:
            sim = 1.
        for i in range(1,5):
            comval = result['sim'+str(i)]
            print result['sense'+str(i)+'_1'],result['sense'+str(i)+'_2'],comval
            if result['same'] == 1:
                if result['sense'+str(i)+'_1'] == result['sense'+str(i)+'_2']:
                    comval += 1.0
                if comval > sim:
                    ans = i
                    sim = comval
            else:
                if result['sense'+str(i)+'_1'] != result['sense'+str(i)+'_2']:
                    comval -= 1.0
                if comval < sim:
                    ans = i
                    sim = comval

    ansselect = ['','A','B','C','D']
    return ansselect[ans]
 
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
