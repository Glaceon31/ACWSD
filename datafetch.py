#-*- coding: utf-8 -*-
from pymongo import MongoClient
from setting import *
import numpy
import argparse
import theano
import theano.tensor as T
import gensim, logging
client = MongoClient()

db = client.wsd
corpusdb = db.corpus
dictdb = db.dict
traindict = db.traindict

parser = argparse.ArgumentParser()
parser.add_argument('keyword')
args = parser.parse_args()

def getsense(sentence, i):
	if len(sentence['senses'][i]) > 0 and sentence['senses'][i] != '[]':
		predictsense = ''
		tagnum = 0
		for sense in sentence['senses'][i]:
			if 'dict' in sense['tagger']:
				predictsense = sense['sense']
				tagnum = maxtagnum
			elif len(sense['tagger']) > tagnum:
				predictsense = sense['sense']
				tagnum = len(sense['tagger'])
		return predictsense
	else:
		return ''



def load_data_word(keyword):
    model = gensim.models.Word2Vec.load(word2vecmodelpath)

    tmpcorpus = corpusdb.find({'sentence': {'$regex':keyword}})

    senselist = []
    
    data_x = []
    data_y = []
    for sentence in tmpcorpus:
    	text = sentence['sentence']
    	for i in range(0,len(text)):
    		word = text[i]
    		if word == keyword:
    			wordsense = getsense(sentence, i)
    			if wordsense != '':
    				if not wordsense in senselist:
    					senselist.append(wordsense)
    				senseindex = senselist.index(wordsense)
    				data_y.append(senseindex)
    				dataarray = numpy.array([])
    				for j in range(i-window_radius,i+window_radius+1):
    					if j < 0 or j >= len(text):
    						dataarray = numpy.hstack((dataarray,numpy.array([0]*50)))
    					else:
    						dataarray = numpy.hstack((dataarray,model[text[j]]))
    				data_x.append(dataarray) 

    print 'sensenum: '+str(len(senselist))
    print 'sentencenum: '+str(tmpcorpus.count())
    print 'traindatanum: '+str(len(data_x))

    trainnumpydata_x = []
    trainnumpydata_y = []
    for i in range(0,int(len(data_x)*0.6)):
        trainnumpydata_x.append(data_x[i])
        trainnumpydata_y.append(numpy.int64(data_y[i]))
    train_set =  (trainnumpydata_x,trainnumpydata_y)
    
    testnumpydata_x = []
    testnumpydata_y = []
    for i in range(int(len(data_x)*0.6),int(len(data_x)*0.8)):
        testnumpydata_x.append(data_x[i])
        testnumpydata_y.append(numpy.int64(data_y[i]))
    test_set = (testnumpydata_x,testnumpydata_y)

    validnumpydata_x = []
    validnumpydata_y = []
    for i in range(int(len(data_x)*0.8),int(len(data_x))):
        validnumpydata_x.append(data_x[i])
        validnumpydata_y.append(numpy.int64(data_y[i]))

    valid_set = (validnumpydata_x,validnumpydata_y)

    def shared_dataset(data_xy, borrow=True):
        data_x, data_y = data_xy
        shared_x = theano.shared(numpy.asarray(data_x,
                                               dtype=theano.config.floatX),
                                 borrow=borrow)
        shared_y = theano.shared(numpy.asarray(data_y,
                                               dtype=theano.config.floatX),
                                 borrow=borrow)
        '''
        print shared_x, shared_y
        print len(data_x), len(data_y)
        print type(data_x[1]), type(data_y[1])
        print data_x[1].shape
        '''
        # When storing data on the GPU it has to be stored as floats
        # therefore we will store the labels as ``floatX`` as well
        # (``shared_y`` does exactly that). But during our computations
        # we need them as ints (we use labels as index, and if they are
        # floats it doesn't make sense) therefore instead of returning
        # ``shared_y`` we will have to cast it to int. This little hack
        # lets ous get around this issue
        return shared_x, T.cast(shared_y, 'int32')

    test_set_x, test_set_y = shared_dataset(test_set)
    valid_set_x, valid_set_y = shared_dataset(valid_set)
    train_set_x, train_set_y = shared_dataset(train_set)

    rval = [(train_set_x, train_set_y), (valid_set_x, valid_set_y),
            (test_set_x, test_set_y)]
    return rval



if __name__ == '__main__':
    load_data_word(args.keyword.decode('utf-8'))