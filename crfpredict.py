#-*- coding: utf-8 -*-
import os
import sys
import time
import copy
import math

import numpy
import argparse
import cPickle
import codecs

import theano
import theano.tensor as T
from theano.tensor.signal import downsample
from theano.tensor.nnet import conv

from logistic_sgd import LogisticRegression
from mlp import HiddenLayer
from convolution import WsdConvPoolLayer
from cnnmodel import cnnmodel
from setting import *
from datafetch import load_data_word, sentence2vector

wordlist = [u'信',u'属',u'之',u'将',u'乃']

def crfpredict(sentence):

    result = []
    for i in range(0, len(sentence)):
    	result.append('')

    for keyword in wordlist:
    	content = ''
        for i in range(0, len(sentence)):
            if sentence[i] == keyword:
                content += sentence[i]+' 1 X\n'
            else:
                content += sentence[i]+' 0 X\n'

        testoutput = codecs.open('crf//test//tmp'+keyword+'_crf.txt', 'wb', 'utf-8')
        testoutput.write(content)
        testoutput.close()
  
        os.system('crf_test -m crf/model/'+keyword.encode('utf-8')+'_crf crf/test/tmp'+keyword.encode('utf-8')+'_crf.txt > crf/output/tmp'+keyword.encode('utf-8')+'_crf.txt')
        inp = open('crf/output/tmp'+keyword.encode('utf-8')+'_crf.txt', 'rb').read()
        words = inp.split('\n')
        for i in range(0, len(sentence)):
            tokens = words[i].split('\t')
            if sentence[i] == keyword:
        		result[i] = tokens[3].decode('utf-8')
    print result
    return result

if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='testcnn')
    parser.add_argument('sentence')

    args = parser.parse_args()

    crfpredict(args.sentence.decode('utf-8'))