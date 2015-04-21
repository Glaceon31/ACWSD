# -*- coding: utf-8 -*-
from lxml import etree
import re
import os
import os.path
import platform
import traceback
from app import *

dictdb = db.dict

wordlist={}
wordnum = 0
tmp = dictdb.find()
for i in tmp:
    wordlist[i['word']] = i['sensexml']
    wordnum += 1
    print wordnum, i['word']