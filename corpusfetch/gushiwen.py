#-*- coding: utf-8 -*-
import re
import os
import urllib2
import codecs

global corpus
#corpus = u''
tagreg = re.compile(u'<.*?>')
replacelist = [u'\u3000', u' ', u'○', u'◎', u'\u007F', u'\r', u'\n']
exclude = [False]*10000
exclude[495] = True
exclude[8375] = True
start = 1
n = 9388

def corpusjoin():
	corpus = u''
	for i in range(start,n+1):
		print i
		if exclude[i]:
			continue
		content = open('gushiwen//rawcorpus-gushiwen'+str(i)+'.txt', 'rb').read()
		corpus = corpus+content.decode('utf-8')
	output = codecs.open('rawcorpus-gushiwen.txt', 'wb', 'utf-8')
	output.write(corpus)
	output.close()

def fetchwebpage(url, m):
	content = urllib2.urlopen(url).read()
	output = open('gushiwenweb//rawcorpus-gushiwen'+str(m)+'.html', 'wb')
	output.write(content)
	output.close()

def fetchguwen(m):
	global corpus
	tmpcorpus = ''
	content = open('gushiwenweb//rawcorpus-gushiwen'+str(m)+'.html', 'rb').read()


	bre = re.compile('<div class="bookvson2">([\s\S]*?</div>)')
	pp = bre.findall(content)[0]
	#print pp

	parare = re.compile('<p>(.*?)</p>')
	paras = parare.findall(pp)

	for para in paras:
		para = para.decode('utf-8')
		for i in replacelist:
			para = para.replace(i,'')
		para = re.sub(u'<.*?>', '', para)
		if para == u'（表略）' or para == '':
			continue
		#corpus += para+'\r\n'
		tmpcorpus += para+'\r\n'

	if tmpcorpus == '':
		onepara = re.compile('</p>([\s\S]*?)</div>')
		maintext = onepara.findall(pp)[0]
		for sentence in maintext.split('<br />'):
			para = sentence.decode('utf-8')
			for i in replacelist:
				para = para.replace(i,'')
			para = re.sub(u'<.*?>', '', para)
			if para == u'（表略）' or para == '':
				continue
			tmpcorpus += para+'\r\n'


	output = codecs.open('gushiwen//rawcorpus-gushiwen'+str(m)+'.txt', 'wb', 'utf-8')
	output.write(tmpcorpus)
	output.close()



'''
for i in range(start,n+1):
	print i
	if exclude[i]:
		continue
	fetchwebpage('http://so.gushiwen.org/guwen/bookv_'+str(i)+'.aspx', i)

fetchguwen(3548)

for i in range(start,n+1):
	print i
	if exclude[i]:
		continue
	fetchguwen(i)
'''
corpusjoin()