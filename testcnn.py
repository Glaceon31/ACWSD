#-*- coding: utf-8 -*-
import os
import sys
import time
import copy
import math

import numpy
import argparse
import cPickle

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
from app import *

wordlist = [u'信',u'属',u'之',u'将',u'乃']

def testcnn(sentence):
    
    result = []

    for i in range(0,len(sentence)):

        if sentence[i] in wordlist:
            savefile = open('model//cnn//'+sentence[i])
            model = cPickle.load(savefile)
            data_x = [sentence2vector(sentence, model.window_radius, model.vector_size,i)]

            test_set_x = theano.shared(numpy.asarray(data_x,
                                               dtype=theano.config.floatX),
                                 borrow=True)

            print test_set_x
            index = T.lscalar()
            output_model = theano.function(
                [index],
                [model.layer2.y_pred],
                givens={
                    model.x: test_set_x[index:(index+1)]
                }
            )

            print sentence, '\t',output_model(0)[0][0]
            result.append(wsdata.senselist[sentence[i]][output_model(0)[0][0]])
        else:
            result.append('')
    return result 

if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='testcnn')
    parser.add_argument('sentence')

    args = parser.parse_args()

    testcnn(args.sentence.decode('utf-8'))
