#-*- coding: utf-8 -*-
import json
from app import *

@app.route('/wsd/<data>', methods=['GET', 'POST'])
def sensedistribute(data):
    global corpus
    sentence = []
    print len(wsdata.wordlist)
    for i in data:
        print repr(i)
        if wsdata.wordlist.has_key(i):
            if corpus.has_key(data):
                predict = False
                for j in range(0, len(corpus[data])):
                    if data[j] == i and corpus[data][j] != '':
                        #print 1
                        sentence.append({'word':i,'sense':wsdata.wordlist[i],'predictsense': corpus[data][j]})
                        predict = True
                if not predict:
                    sentence.append({'word':i,'sense':wsdata.wordlist[i],'predictsense':''})
            else:
                sentence.append({'word':i,'sense':wsdata.wordlist[i],'predictsense':''})
        else:
            sentence.append({'word':i,'sense':''})
    return json.dumps(sentence)

@app.route('/update/<jsondata>', methods=['GET', 'POST'])
def update(jsondata):
    global corpus
    data = json.loads(jsondata)
    if corpus.has_key(data['sentence']):
        for i in range(0, len(data['sentence'])):
            if data['sentence'][i] == data['word']:
                corpus[data['sentence']][i] = data['sense']
    else:
        corpus[data['sentence']] = []
        for word in data['sentence']:
            if word == data['word']:
                corpus[data['sentence']].append(data['sense'])
            else:
                corpus[data['sentence']].append('')
    cfile = open(u'corpus//corpus.txt', 'wb')
    cfile.write(json.dumps(corpus))
    cfile.close()
    return '1'
