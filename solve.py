#-*- coding: utf-8 -*-
import codecs
import traceback
import json
import re
import numpy as np
from testcnn import testcnn, testcnnp, testcnn_one, testcnnp_one
import numpy
import os
from gensim.models import Word2Vec
from scipy import spatial
import sys

word2vec = Word2Vec.load('/global-mt/zjc/gaokao/autotag/gensim/word2vec.model')

def get_keyword(stem):
    kre = re.compile('<point>(.*?)</point>')
    result = kre.findall(stem)
    if len(result) >= 0:
        return result[0]
    else:
        return '' 


def geteditdistance(a,b):
    a = removepunc(a)
    b = removepunc(b)
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

def gram(a,b):
    a = removepunc(a)
    b = removepunc(b)
    a = segment(a)
    b = segment(b)
    result = 0
    for i in a.split(' '):
        for j in b.split(' '):
            if i == j:
                result += 1
                break  
    return result

def max_matching(a,b):
    a = removepunc(a)
    b = removepunc(b)
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

def solveprocess(jsondata):
    #print jsondata
    jsondata = jsondata.replace('**(point,0,Null)**', '<point>').replace('**(point,1,Null)**','</point>')
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
        print 'XML format error'
        result['error'] = u'XML格式错误'
        return json.dumps(result)
    try:
        if u'解释' in data['stem'] and not data.has_key('substem'):#(u'下列语句' in data['stem'] or u'下列句子' in data['stem']):
            result['type'] = 'taggingjudge'
            for i in range(1,5):
                #print i
                keyword = get_keyword(data['select'+str(i)])
                sentence = data['select'+str(i)].split('$$')[0].replace('<point>','').replace('</point>','')
                result['keyword'+str(i)] = keyword
                judgesense = data['select'+str(i)].split('$$')[1]
                position = sentence.index(keyword)
                cnnpredictlist = testcnn_one(sentence,position)
                cnnp = testcnnp_one(sentence,position)
                if cnnp[0] == '':#cnnp[sentence.index(keyword)] == '':
                    p = ''
                else:
                    p = max(cnnp[0])#max(cnnp[sentence.index(keyword)])
                sense = cnnpredictlist[0]
                #sense = cnnpredictlist[sentence.index(keyword)]
                result['judgesense'+str(i)] = judgesense
                result['sense'+str(i)] = sense
                result['p'+str(i)] = p
                #choose wrong
                if u'不正确' in data['stem']:
                    result['same'] = 0
                else:
                    result['same'] = 1
            result['success'] = 1
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
        elif u'组句' in data['stem'] or u'组语句' in data['stem'] or u'组词语' in data['stem'] or u'下列句子' in data['stem'] or u'下列各句' in data['stem'] or u'下列语句' in data['stem']:
            result['type'] = 'sentence_pair'
            for i in range(1,5):
                keyword = get_keyword(data['select'+str(i)])
                sentencepair = data['select'+str(i)].replace('<point>','').replace('</point>','').split('$$')
                sentence1 = sentencepair[0]
                sentence2 = sentencepair[1]
                result['keyword'+str(i)] = keyword
                #print keyword, sentence1, sentence2
                position1 = sentence1.index(keyword)
                position2 = sentence2.index(keyword)
                cnnpredictlist1 = testcnn_one(sentence1,position1)
                cnnpredictlist2 = testcnn_one(sentence2,position2)
                cnnp1 = testcnnp_one(sentence1,position1)
                cnnp2 = testcnnp_one(sentence2,position2)
                '''
                cnnpredictlist1 = testcnn(sentence1)
                cnnpredictlist2 = testcnn(sentence2)
                cnnp1 = testcnnp(sentence1)
                cnnp2 = testcnnp(sentence2)
                '''
                #print cnnp1
                #print cnnp2
                #sense1 = cnnpredictlist1[sentence1.index(keyword)]
                #p1 = cnnp1[sentence1.index(keyword)]
                sense1 = cnnpredictlist1[0]
                p1 = cnnp1[0]
                result['sense'+str(i)+'_1'] = sense1
                #sense2 = cnnpredictlist2[sentence2.index(keyword)]
                #p2 = cnnp2[sentence2.index(keyword)]
                sense2 = cnnpredictlist2[0]
                p2 = cnnp2[0]
                result['sense'+str(i)+'_2'] = sense2
                #print p1
                #print p2
		#print np.dot(p1, p2)
                result['sim'+str(i)] = np.dot(p1, p2)
            #choose correct
            if u'相同' in data['stem'] and not u'不' in data['stem']:
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
        return json.dumps(result)
    return result


def cos_sim(v1,v2):
	return 1-spatial.distance.cosine(v1,v2)

punctuation = u'“，。！？,.?!”";:：；'

def removepunc(text):
	result = text
	for punc in punctuation:
		result = result.replace(punc, '')
	return result	

def segment(text):
	thulac = '/global-mt/zjc/thulac/thulac/thulac'
	segfile = codecs.open('toseg', 'w', 'utf-8')
	segfile.write(text)
	segfile.close()
	os.system(thulac+' -seg_only < toseg > segmented')
	result = codecs.open('segmented', 'r', 'utf-8').read()
	os.system('rm toseg')
	os.system('rm segmented')
	return result.replace('\n','')

def sim(p1,p2):
	segp1 = segment(p1)
	segp2 = segment(p2)
	vec1 = [0]*500
	for wd in segp1.split(' '):
		if wd in punctuation:
			continue
		try:
			vec1 += word2vec[wd]
		except:
			pass
	vec2 = [0]*500
	for wd in segp2.split(' '):
		if wd in punctuation:
			continue
		try:
			vec2 += word2vec[wd]
		except:
			pass
	return cos_sim(vec1,vec2)

def solve(xml, verbose=False):
	result = solveprocess(xml)
	choice = ['A', 'B', 'C', 'D']
	if result['type'] == 'tagging':
		score_sim = [0.]*4
		result['same'] = 1
		if verbose:
			print result['sense']
		for i in range(4):
			matchscore = gram(result['sense'], result['select'+str(i+1)])
			distpenal = min([geteditdistance(s, result['select'+str(i+1)]) for s in re.split(u'；|，',result['sense'])])#/len(result['select'+str(i+1)])
			score_sim[i] = 5*matchscore-distpenal+0.001*sim(result['sense'], result['select'+str(i+1)])
			if verbose:
				print matchscore,distpenal,sim(result['sense'], result['select'+str(i+1)])
	elif result['type'] == 'taggingjudge':
		score_sim = [0.]*4
		for i in range(4):
			matchscore = gram(result['sense'+str(i+1)], result['judgesense'+str(i+1)])
			distpenal = min([geteditdistance(s, result['judgesense'+str(i+1)]) for s in re.split(u'；|，',result['sense'+str(i+1)])])#/len(result['judgesense'+str(i+1)])
			score_sim[i] = 5*matchscore-distpenal+0.001*sim(result['sense'+str(i+1)], result['judgesense'+str(i+1)])
			if verbose:
				print result['sense'+str(i+1)],matchscore,distpenal,sim(result['sense'+str(i+1)], result['judgesense'+str(i+1)])
	elif result['type'] == 'sentence_pair':
		score_sim = [0.]*4
		for i in range(4):
			if result['sense'+str(i+1)+'_1'] == result['sense'+str(i+1)+'_2']:
				score_sim[i] += 0.
			score_sim[i] += result['sim'+str(i+1)]
	else:
		return 'no!!!'
	if result['same'] == 1:
		ans = numpy.argmax(score_sim)
	else:
		ans = numpy.argmin(score_sim)
	if verbose:
		print result['type'],score_sim
	return result['type'],result['same'],choice[ans]
			 

if __name__ == '__main__':
	if len(sys.argv) >= 2:
		xml = codecs.open('problems/'+sys.argv[1]+'.xml', 'r', 'GBK').read()
		ans = solve(xml,verbose=True)
		exit()
	#print open('problems/gaokao_id','r').read()
	gaokao_id = json.loads(open('problems/gaokao_id','r').read())
	moni_id = json.loads(open('problems/moni_id','r').read())
	answers1 = []
	for i in gaokao_id:
		
		xml = codecs.open('problems/bj'+i[0]+'.xml','r','GBK').read()#.decode('gbk')
		#print repr(xml)
		ans = solve(xml)
		answers1.append([i[0],ans,i[1],ans[-1]==i[1]])
	answers2 = []
	for i in moni_id:
		xml = codecs.open('problems/mn'+i[0]+'.xml','r','GBK').read()
		ans = solve(xml)
		answers2.append([i[0],ans,i[1],ans[-1]==i[1]])
	print 'gaokao'
	for i in answers1:
		print i
	print 'moni'
	for i in answers2:
		print i
		
