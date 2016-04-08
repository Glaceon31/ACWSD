# -*- coding: utf-8 -*-
import os
import os.path
import json

from traincnnmulti import trainword
from pymongo import MongoClient
client = MongoClient()

db = client.wsd

dictdb = db.dict


tmp = dictdb.find()
print tmp.count()
wordnum = 0
trainnum = 0
failnum = 0
for i in tmp:
	wordnum += 1
	print wordnum, i['word'] 
	if os.path.exists('model/cnn/'+i['word']):
		print 'have'
	else:
		trainnum += 1
		#trainword(i['word'],4,0.01,500,1,50,1,250,1,1,2000,250,0)
		
		try:
			trainword(i['word'],4,0.01,500,1,50,1,250,1,1,2000,250,0)
		except:
			failnum += 1
		

print 'trainnum:', trainnum
print 'failnum:', failnum 