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

def adddict():
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

cfile = open(u'corpus//corpus.txt','rb')
global corpus
corpus = json.loads(cfile.read())
cfile.close()
sentencenum = 0
def addcorpus():
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

addcorpus()