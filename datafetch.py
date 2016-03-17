#-*- coding: utf-8 -*-
from pymongo import MongoClient
from setting import *
import numpy
import argparse
import theano
import codecs
import json
import theano.tensor as T
import gensim, logging
client = MongoClient()

db = client.wsd
corpusdb = db.corpus
dictdb = db.dict
traindict = db.traindict

def sentence2vector(sentence, window_radius, vector_size, i):  
    word2vecmodel = gensim.models.Word2Vec.load(word2vecmodelpath+'_'+str(vector_size))               
    dataarray = numpy.array([])
    for j in range(i-window_radius,i+window_radius+1):
        if j < 0 or j >= len(sentence):
            dataarray = numpy.hstack((dataarray,numpy.array([0]*vector_size)))
        else:
            dataarray = numpy.hstack((dataarray,word2vecmodel[sentence[j]]))
    print dataarray
    return dataarray

def normalize(a):
    sqr = 0
    for i in range(0,len(a)):
        sqr += a[i]*a[i]
    result = [a[i]/sqr for i in range(0, len(a))]
    return result

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

def sensemap(sense):
    maplist = {u'用在“前”、“后”、“内”、“外”等词语和它们的修饰语之间，表示对方位、时间、范围等的限制': u'用在定语和中心词之间，表示修饰、领属的关系，相当于“的”'}
    if maplist.has_key(sense):
        return maplist[sense]
    else:
        return sense

def produce_senselist(keyword):
    print 'produce senselist for', keyword
    tmpcorpus = corpusdb.find({'sentence': {'$regex':keyword}})

    senselist = []
    sensecount = []

    for sentence in tmpcorpus:
        text = sentence['sentence']
        for i in range(0,len(text)):
            word = text[i]
            if word == keyword:
                wordsense = getsense(sentence, i)
                if wordsense != '':
                    wordsense = sensemap(wordsense)
                    sen = ''
                    try:
                        if not wordsense in senselist:
                            senselist.append(wordsense)
                    except:
                        a = 1

    output = codecs.open('senselist/'+keyword+'.txt', 'wb', 'utf-8')
    output.write(json.dumps(senselist))
    output.close()
    return senselist

def get_senselist(keyword):
    try:
        input = codecs.open('senselist/'+keyword+'.txt', 'rb', 'utf-8')
        senselist = json.loads(input.read())
        input.close()
    except:
        senselist = produce_senselist(keyword)
    return senselist

def load_data_word(keyword, window_radius, vector_size, sequence = 0, nomralized = False, border = False, showsentence = False, outputtxt = False):
    print 'fetching data for '+keyword
    model = gensim.models.Word2Vec.load(word2vecmodelpath+'_'+str(vector_size))

    tmpcorpus = corpusdb.find({'sentence': {'$regex':keyword}})

    senselist = []
    sensecount = []

    outputcontent = ''
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
                    wordsense = sensemap(wordsense)
                    sen = ''
                    if showsentence:
                        print text, wordsense
                    if outputtxt:
                        outputcontent += wordsense+'\t'+str(i+1)+'\t'+text+'\r\n'
                    try:
                        if not wordsense in senselist:
                            senselist.append(wordsense)
                            sensecount.append(0)
                        senseindex = senselist.index(wordsense)
                        sensecount[senseindex] += 1
                    
                        dataarray = numpy.array([])
                        for j in range(i-window_radius,i+window_radius+1):
                            if j < 0 or j >= len(text):
                                dataarray = numpy.hstack((dataarray,numpy.array([0]*vector_size)))
                                sen = sen+' '
                            else:
                                sen = sen+text[j]
                                if nomralized:
                                    dataarray = numpy.hstack((dataarray,normalize(model[text[j]])))
                                else:
                                    dataarray = numpy.hstack((dataarray,model[text[j]]))
                        data_y.append(senseindex)
                        data_x.append(dataarray)
                        data_sentence.append(sen)
                    except:
                        a = 1

    if outputtxt:
        output = codecs.open('tagged/'+keyword+'.txt', 'wb', 'utf-8')
        output.write(outputcontent)
        output.close()
    print 'sensenum: '+str(len(senselist))
    print 'sentencenum: '+str(tmpcorpus.count())
    print 'traindatanum: '+str(len(data_x))
    #for i in range(0, len(data_sentence)):
    #   print data_sentence[i], senselist[data_y[i]]
    print senselist
    print sensecount

    trainnumpydata_x = []
    trainnumpydata_y = []
    trainsentence = []
    
    testnumpydata_x = []
    testnumpydata_y = []
    testsentence = []       

    validnumpydata_x = []
    validnumpydata_y = []
    validsentence = []

    for i in range(0, len(data_x)):
        if i % 5 == (3+sequence) % 5:
            testnumpydata_x.append(data_x[i])
            testnumpydata_y.append(numpy.int64(data_y[i]))
            testsentence.append(data_sentence[i])
        elif i % 5 == (4+sequence) % 5:
            validnumpydata_x.append(data_x[i])
            validnumpydata_y.append(numpy.int64(data_y[i]))
            validsentence.append(data_sentence[i])
        else:
            trainnumpydata_x.append(data_x[i])
            trainnumpydata_y.append(numpy.int64(data_y[i]))
            trainsentence.append(data_sentence[i])

    train_set =  (trainnumpydata_x,trainnumpydata_y)
    test_set = (testnumpydata_x,testnumpydata_y)
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
    get_senselist(args.keyword.decode('utf-8'))
    #load_data_word(args.keyword.decode('utf-8'), 3, 50, showsentence = True, outputtxt = True)