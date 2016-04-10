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

def getwordlist():
	tmp = dictdb.find()
	print tmp.count()
	result = []
	for i in tmp:
		result.append(i['word'])
	return result

def refreshdict():
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

