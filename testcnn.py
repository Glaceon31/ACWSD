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


wordlist = [u'信',u'属',u'之',u'将',u'乃']
senselist = {}
senselist[u'信'] = [u'\u8bb2\u4fe1\u7528', u'\u76f8\u4fe1\uff1b\u4fe1\u4efb', u'\u4fe1\u7528', u'\u4efb\u968f\uff1b\u968f\u610f', u'\u786e\u5b9e\uff1b\u7684\u786e', u'\u4f7f\u8005\uff1b\u9001\u4fe1\u7684\u4eba', u'\u6d88\u606f\uff1b\u97f3\u8baf', u'\u901a\u201c\u4f38\u201d', u'\u5feb\u4fe1\uff1b\u4fe1\u4ef6', u'\u4fe1\u7269\uff1b\u51ed\u8bc1', u'\u5b9e\u5728\u7684\uff1b\u771f\u5b9e\u7684', u'\u8a00\u8bed\u771f\u5b9e\uff1b\u8bda\u5b9e', u'\u8bda\u5b9e\u7684\u3001\u53ef\u9760\u7684', u'\u4eba\u540d', u'\u5151\u73b0', u'\u53d6\u4fe1']
senselist[u'属']= [u'\u64b0\u5199', u'\u8ddf\u7740', u'\u5bb6\u5c5e', u'\u901a\u201c\u5631\u201d\uff0c\u770b', u'\u5f52\u5c5e\uff1b\u96b6\u5c5e', u'\u90e8\u5c5e', u'\u7c7b\uff1b\u8f88', u'\u901a\u201c\u5631\u201d', u'\u8fde\u63a5', u'\u7ba1\u8f96', u'\u76f8\u4f3c', u'\u6070\u9022']
senselist[u'之']= [u'\u7b2c\u4e09\u4eba\u79f0\u4ee3\u8bcd\uff0c\u76f8\u5f53\u4e8e\u201c\u4ed6\u201d\u3001\u201c\u5b83\u201d\u3001\u201c\u5b83\u4eec\u201d\u3001\u201c\u4ed6\u4eec\u201d\u7b49', u'\u7528\u5728\u5b9a\u8bed\u548c\u4e2d\u5fc3\u8bcd\u4e4b\u95f4\uff0c\u8868\u793a\u4fee\u9970\u3001\u9886\u5c5e\u7684\u5173\u7cfb\uff0c\u76f8\u5f53\u4e8e\u201c\u7684\u201d', u'\u7528\u5728\u4e3b\u8c13\u4e4b\u95f4\uff0c\u53d6\u6d88\u53e5\u5b50\u72ec\u7acb\u6027\uff0c\u4e00\u822c\u4e0d\u5fc5\u8bd1\u51fa', u'\u5230\u2026\u2026\u53bb', u'\u7b2c\u4e8c\u4eba\u79f0\u4ee3\u8bcd\uff0c\u76f8\u5f53\u4e8e\u201c\u4f60\u201d\u3001\u201c\u60a8\u201d', u'\u5b9a\u8bed\u540e\u7f6e\u7684\u6807\u5fd7', u'\u6307\u793a\u4ee3\u8bcd\uff0c\u76f8\u5f53\u4e8e\u201c\u8fd9\u4e2a\u201d\u3001\u201c\u8fd9\u201d\u3001\u201c\u8fd9\u79cd\u201d\u7b49', u'\u7528\u5bbe\u8bed\u524d\u7f6e\u7684\u6807\u5fd7', u'\u6307\u4ee3\u8bf4\u8bdd\u8005\u672c\u4eba\u6216\u542c\u8bdd\u8005\u7684\u5bf9\u65b9', u'\u8865\u8bed\u7684\u6807\u5fd7', u'\u7528\u5728\u8868\u793a\u65f6\u95f4\u7684\u526f\u8bcd\u540e\uff0c\u8865\u8db3\u97f3\u8282\uff0c\u6ca1\u6709\u5b9e\u4e49', u'\u65e0\u5b9e\u4e49']
senselist[u'将']= [u'\u4f7f\u2026\u2026\u4e3a\u5c06\u519b', u'\u7528\u4e8e\u52a8\u8bcd\u540e\uff0c\u4ee5\u52a9\u8bed\u6c14', u'\u5c06\u9886\uff1b\u5c06\u5e05', u'\u5e26\u9886\uff1b\u643a\u5e26', u'\u548c\uff1b\u4e0e', u'\u4e14\uff1b\u53c8', u'\u5c06\u5c31\uff1b\u968f\u987a', u'\u628a\uff1b\u7528', u'\u5c06\u8981\uff1b\u5c31\u8981', u'\u62ff\uff1b\u6301', u'\u5047\u82e5\uff1b\u5982\u679c', u'\u7edf\u7387\uff1b\u7387\u9886', u'\u60f3\u8981\uff1b\u6253\u7b97', u'\u6291\u6216\uff1b\u8fd8\u662f', u'\u8bf7\uff0c\u613f', u'\u6400\u6276\uff1b\u6276\u6301']
senselist[u'乃']= [u'\u4e8e\u662f\uff1b\u5c31', u'\u751a\u81f3', u'\u8868\u5224\u65ad\uff0c\u662f', u'\u624d', u'\u4ec5\u4ec5\uff1b\u53ea', u'\u8fd9\uff1b\u8fd9\u6837', u'\u7adf\u7136\uff1b\u5374', u'\u4f60(\u7684)\uff1b\u4f60\u4eec(\u7684)', u'\u53c8', u'\u5e94\u8be5']

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
            result.append(senselist[sentence[i]][output_model(0)[0][0]])
        else:
            result.append('')
    return result 

if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='testcnn')
    parser.add_argument('sentence')

    args = parser.parse_args()

    testcnn(args.sentence.decode('utf-8'))
