# -*- coding: utf-8 -*-
from lxml import etree
import re
import os
import os.path
import platform

def parsexml(xml):
    senses = []
    return senses

wordlist={}
wordnum = 0
failnum = 0
for parents,dirnames,filenames in os.walk(r'dict'):
    for f in filenames:
        #try:
        word = {}
        word['senses'] = open('dict//'+f,'rb').read()
        if platform.system() == 'Windows':
            wordlist[os.path.splitext(f)[0].decode('gbk')] = word
            wordnum += 1
            print wordnum ,os.path.splitext(f)[0].decode('gbk')
        else:
            wordlist[os.path.splitext(f)[0].decode('utf-8')] = word
            wordnum += 1
            print wordnum ,os.path.splitext(f)[0].decode('utf-8')
        #except:
        #    failnum += 1
        #    print 'fail: '+f
#print wordnum
#print failnum
#print wordlist.has_key(u'1')
#print repr(u'粉')
