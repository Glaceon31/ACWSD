# -*- coding: utf-8 -*-
import os
import os.path
import json
import string
import sys

from traincnnmulti import trainword
from pymongo import MongoClient
client = MongoClient()

db = client.wsd

dictdb = db.dict


tmp = list(dictdb.find())
print len(tmp)
wordnum = 0
trainnum = 0
failnum = 0
start = min(string.atoi(sys.argv[1]), len(tmp))
end = min(string.atoi(sys.argv[2]), len(tmp))
#trainword(u'我',4,0.01,500,1,50,1,250,1,1,2000,250,0)
for i in range(start,end):
	wordnum += 1
	print wordnum, i, tmp[i]['word'] 
	if os.path.exists('model/cnn/'+tmp[i]['word']):
		print 'have'
	else:
		trainnum += 1
		#trainword(i['word'],4,0.01,500,1,50,1,250,1,1,2000,250,0)
		
		try:
			trainword(tmp[i]['word'],4,0.01,500,1,50,1,250,1,1,2000,250,0)
		except:
			failnum += 1
		

print 'trainnum:', trainnum
print 'failnum:', failnum 
