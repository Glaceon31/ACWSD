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
parser.add_argument('-v', '--vector_size', action="store", type=int,default=50)
parser.add_argument('-s', '--simword', action="store")

args = parser.parse_args()

def trainewmodel(vector_size):
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
	model.save(word2vecmodelpath+'_'+str(vector_size))
	
def testsimiliarity(simword, vector_size):
	model = gensim.models.Word2Vec.load(word2vecmodelpath+'_'+str(vector_size))
	for i in model.most_similar(positive=[simword]):
		print i[0], i[1]
	return 

if args.new:
	trainewmodel(args.vector_size)
	exit()
else:
	if args.simword:
		testsimiliarity(args.simword.decode('utf-8'),args.vector_size)