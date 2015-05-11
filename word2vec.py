#-*- coding: utf-8 -*-
import gensim, logging
import argparse
from pymongo import MongoClient
from setting import *
client = MongoClient()
db = client.wsd
corpusdb = db.corpus

dbsentences = corpusdb.find()

parser = argparse.ArgumentParser()
parser.add_argument('-n', '--new', action="store_true")
parser.add_argument('-s', '--similarity', action="store_true")
parser.add_argument('simword')

args = parser.parse_args()

def trainewmodel():
	totaltoken = 0
	tls = 0
	sentences = []
	for sentence in dbsentences:
		sen = sentence['sentence']
		tls += len(sen)
		totaltoken += len(','.join(sen).split(','))
		sentences.append(','.join(sen).split(','))
	print totaltoken, tls, len(sentences), sentences[2]
	model = gensim.models.Word2Vec(sentences, size=vector_size, min_count = 2)
	model.save(word2vecmodelpath)
	
def testsimiliarity(simword):
	model = gensim.models.Word2Vec.load(word2vecmodelpath)
	for i in model.most_similar(positive=[simword]):
		print i[0], i[1]
	return 

if args.new:
	trainewmodel()
	exit()
else:
	if args.similarity:
		testsimiliarity(args.simword.decode('utf-8'))