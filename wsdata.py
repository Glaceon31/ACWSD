# -*- coding: utf-8 -*-
from lxml import etree
import re
import os
import os.path
import platform
import traceback
from app import *

dictdb = db.dict

global wordlist

keywordlist = [u'信',u'属',u'之',u'将',u'乃']
global senselist

def refreshdict():
	global senselist
	senselist = {}
	for keyword in keywordlist:
		datasets = load_data_word(keyword, 1, 50, sequence = 0)
		senselist[keyword] = datasets[1]
	global wordlist
	wordlist = {}
	wordnum = 0
	tmp = dictdb.find()
	print tmp.count()
	for i in tmp:
		wordlist[i['word']] = {}
		wordlist[i['word']]['dictsense'] = i['sensexml']
		#print wordlist[i['word']]
		if i.has_key('usersense'):
			wordlist[i['word']]['usersense'] = i['usersense']
		else:
			wordlist[i['word']]['usersense'] = []
		wordnum += 1
		print wordnum, i['word'] 

refreshdict()

