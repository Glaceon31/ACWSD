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



def load_data_word(keyword, window_radius):
    print 'fetching data for '+keyword
    model = gensim.models.Word2Vec.load(word2vecmodelpath)

    tmpcorpus = corpusdb.find({'sentence': {'$regex':keyword}})

    senselist = []
    
    data_x = []
    data_y = []
    data_sentence = []
    for sentence in tmpcorpus:
        text = sentence['sentence']
        for i in range(0,len(text)):
            word = text[i]
            if word == keyword:
                wordsense = getsense(sentence, i)
                if wordsense != '':
                    sen = ''
                    try:
                        if not wordsense in senselist:
                            senselist.append(wordsense)
                        senseindex = senselist.index(wordsense)
                    
                        dataarray = numpy.array([])
                        for j in range(i-window_radius,i+window_radius+1):
                            if j < 0 or j >= len(text):
                                dataarray = numpy.hstack((dataarray,numpy.array([0]*50)))
                                sen = sen+' '
                            else:
                                sen = sen+text[j]
                                dataarray = numpy.hstack((dataarray,model[text[j]]))
                        data_y.append(senseindex)
                        data_x.append(dataarray)
                        data_sentence.append(sen)
                    except:
                        a = 1


    print 'sensenum: '+str(len(senselist))
    print 'sentencenum: '+str(tmpcorpus.count())
    print 'traindatanum: '+str(len(data_x))
    for i in data_sentence:
        print i

    trainnumpydata_x = []
    trainnumpydata_y = []
    trainsentence = []
    for i in range(0,int(len(data_x)*0.6)):
        trainnumpydata_x.append(data_x[i])
        trainnumpydata_y.append(numpy.int64(data_y[i]))
        trainsentence.append(data_sentence[i])
    train_set =  (trainnumpydata_x,trainnumpydata_y)
    
    testnumpydata_x = []
    testnumpydata_y = []
    testsentence = []
    for i in range(int(len(data_x)*0.6),int(len(data_x)*0.8)):
        testnumpydata_x.append(data_x[i])
        testnumpydata_y.append(numpy.int64(data_y[i]))
        testsentence.append(data_sentence[i])
    test_set = (testnumpydata_x,testnumpydata_y)

    validnumpydata_x = []
    validnumpydata_y = []
    validsentence = []
    for i in range(int(len(data_x)*0.8),int(len(data_x))):
        validnumpydata_x.append(data_x[i])
        validnumpydata_y.append(numpy.int64(data_y[i]))
        validsentence.append(data_sentence[i])

    valid_set = (validnumpydata_x,validnumpydata_y)

    #insert senselist into db
    tmptdict = traindict.find_one({'word':keyword})
    if not tmptdict:
        traindict.insert_one({'word':keyword, 'senses':senselist})
    else:
        traindict.update_one({'word':keyword}, {'$set':{'senses': senselist}})

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

    rval = [(train_set_x, train_set_y, trainsentence), (valid_set_x, valid_set_y, validsentence),
            (test_set_x, test_set_y, testsentence)]
    return (rval, senselist)



if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('keyword')
    args = parser.parse_args()
    load_data_word(args.keyword.decode('utf-8'), 3)