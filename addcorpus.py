# -*- coding: utf-8 -*-
from lxml import etree
import re
import os
import os.path
import platform
import traceback
import json

from pymongo import MongoClient
client = MongoClient()

db = client.wsd

corpusdb = db.corpus
dictdb = db.dict

def adddict0():
	wordlist={}
	wordnum = 0
	failnum = 0
	for parents,dirnames,filenames in os.walk(r'dict'):
		for f in filenames:
			word = {}
			word['senses'] = open('dict//'+f,'rb').read()
			ordname = ''
			if platform.system() == 'Windows':
				wordname = os.path.splitext(f)[0].decode('gbk')
			else:
				wordname = os.path.splitext(f)[0].decode('utf-8')
			try:
				tmp = dictdb.find_one({'word': wordname})
				print wordnum
				if not tmp:
					newword = {'word': wordname, 'sensexml': word['senses']}
					wordnum += 1
					dictdb.insert_one(newword)
			except:
				traceback.print_exc()
				print 'dberror'
				return 'dberror'

def adddict():
	wordnum = 0
	failnum = 0
	words = json.loads(open('dict//dict.txt', 'rb').read())
	for word in words:
		tmp = dictdb.find_one({'word' :word['word']})
		if not tmp:
			wordnum += 1
			print wordnum
			dictdb.insert_one(word)

def extractdict():
	tmp = dictdb.find()
	words = []
	for i in tmp:
		word = {}
		word['word'] = i['word']
		word['sensexml'] = i['sensexml']
		words.append(word)
	output = open('dict//dictex.txt', 'wb')
	output.write(json.dumps(words))
	output.close()
'''
cfile = open(u'corpus//corpus.txt','rb')
global corpus
corpus = json.loads(cfile.read())
cfile.close()
sentencenum = 0
'''
def addcorpus0():
	global corpus
	for sentence, sense in corpus.items():
		#print sentence, sense
		try:
			tmp = corpusdb.find_one({'sentence' : sentence})
			newsentence = {'sentence':sentence}
			if not tmp:
				senses = []
				for i in range(0, len(sentence)):
					senses.append('[]')
					if sense[i] != '':
						senses[i] = [{'sense':sense[i],'tagger':['0']}]
				newsentence['senses'] = senses
				newsentence['adder'] = 'dict'
				corpusdb.insert_one(newsentence)
			else:
				senses = tmp['senses']
				for i in range(0, len(sentence)):
					if sense[i] != '':
						senses[i] = [{'sense':sense[i],'tagger':['0']}]
				corpusdb.update_one({'sentence': sentence}, {'$set':{'senses':senses}})
		except:
			traceback.print_exc()
			print 'dberror'
			return 'dberror'

def addcorpus():
	sentencenum = 0
	failnum = 0
	sentences = json.loads(open('corpus//corpus.txt', 'rb').read())
	for sentence in sentences:
		tmp = corpusdb.find_one({'sentence' :sentence['sentence']})
		if not tmp:
			sentencenum += 1
			print sentencenum
			corpusdb.insert_one(sentence)

def extractcorpus():
	tmp = corpusdb.find()
	sentences = []
	for i in tmp:
		sentence = {}
		sentence['sentence'] = i['sentence']
		sentence['senses'] = i['senses']
		sentence['adder'] = i['adder']
		sentences.append(sentence)
	output = open('corpus//corpusex.txt', 'wb')
	output.write(json.dumps(sentences))
	output.close()

def addrawcorpus():
        sentencenum = 0
	failnum = 0
	sentences = open('corpus//rawcorpus-midschool.txt', 'rb').read().split('\r\n')
	for sentence in sentences:
                tmp = corpusdb.find_one({'sentence' :sentence})
                if not tmp:
                        sentencenum += 1
                        print sentencenum
                        newsentence = {}
                        newsentence['sentence'] = sentence
                        newsentence['adder'] = 'Grit'
                        newsentence['source'] = 'midschool'
                        newsentence['senses'] = []
                        for i in sentence:
                                newsentence['senses'].append([])
                        corpusdb.insert_one(newsentence)
                        

addrawcorpus()
