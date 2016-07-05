# -*- coding: utf-8 -*-
import os
import os.path
import json
import argparse

from traincnnmulti import trainword
from pymongo import MongoClient
client = MongoClient()

db = client.wsd

dictdb = db.dict
parser = argparse.ArgumentParser()
parser.add_argument('keyword')
args = parser.parse_args()

try:
	trainword(args.keyword.decode('utf-8'),4,0.01,500,1,50,1,250,1,1,2000,250,0)
except:
	print 'fail'
		
 