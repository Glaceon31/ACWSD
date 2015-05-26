#-*- coding: utf-8 -*-
import os
import sys
import time
import copy
import math

import numpy
import argparse

import theano
import theano.tensor as T
from theano.tensor.signal import downsample
from theano.tensor.nnet import conv

from logistic_sgd import LogisticRegression
from mlp import HiddenLayer
from convolution import WsdConvPoolLayer
from setting import *
from datafetch import load_data_word

from pymongo import MongoClient
client = MongoClient()

db = client.wsd
dictdb = db.dict

def trainword(keyword, window_radius = 3, learning_rate = 0.1, n_epochs = 10,batch_size = 1, nkerns = 1,filter_height=3,filter_width = 50, pool_height=1,pool_width = 1, loginput_num = 50, vector_size = 50, normalized = False):

    print '==training parameters=='
    print 'window_radius: '+str(window_radius)
    print 'vector_size: '+str(vector_size)
    print 'filter_height: '+str(filter_height)
    print 'filter_width: '+str(filter_width)
    print 'pool_height: '+str(pool_height)
    print 'pool_width: '+str(pool_width)
    print 'nkerns: '+str(nkerns)
    print 'loginput_num: '+str(loginput_num)
    print 'learning_rate: '+str(learning_rate)
    print 'n_epochs: '+str(n_epochs)
    print 'batch_size: '+str(batch_size)

    rng = numpy.random.RandomState(23455)
    datasets = load_data_word(keyword, window_radius, vector_size, normalized)

    train_set_x, train_set_y, trainsentence = datasets[0][0]
    valid_set_x, valid_set_y, validsentence = datasets[0][1]
    test_set_x, test_set_y, testsentence = datasets[0][2]

    senselist = datasets[1]

    n_train_batches = train_set_x.get_value(borrow=True).shape[0]
    n_valid_batches = valid_set_x.get_value(borrow=True).shape[0]
    n_test_batches = test_set_x.get_value(borrow=True).shape[0]
    n_train_batches /= batch_size
    n_valid_batches /= batch_size
    n_test_batches /= batch_size
    print n_train_batches, n_valid_batches, n_test_batches

    index = T.lscalar()

    x = T.matrix('x')   
    y = T.ivector('y')

    print '... building the model for '+keyword

    layer0_input = x.reshape((batch_size, 1, 2*window_radius+1, vector_size))

    layer0 = WsdConvPoolLayer(
        rng,
        input=layer0_input,
        image_shape=(batch_size, 1, 2*window_radius+1, vector_size),
        filter_shape=(nkerns, 1, filter_height, filter_width),
        poolsize=(pool_height, pool_width)
    )

    layer1_input = layer0.output.flatten(2)
    #layer1_input = layer0_input.flatten(2)

    layer1 = HiddenLayer(
        rng,
        input=layer1_input,
        #n_in=(2*window_radius+1)*(vector_size+1-filter_width+1-pool_width),
        n_in= nkerns * int((2*window_radius+2-filter_height)/float(pool_height))*int((vector_size+1-filter_width)/float(pool_width)),
        n_out=loginput_num,
        activation=T.tanh
    )

    layer2 = LogisticRegression(input=layer1.output, n_in=loginput_num, n_out=20)

    cost = layer2.negative_log_likelihood(y)

    test_model = theano.function(
        [index],
        layer2.errors(y),
        givens={
            x: test_set_x[index * batch_size: (index + 1) * batch_size],
            y: test_set_y[index * batch_size: (index + 1) * batch_size]
        }
    )

    validate_model = theano.function(
        [index],
        layer2.errors(y),
        givens={
            x: valid_set_x[index * batch_size: (index + 1) * batch_size],
            y: valid_set_y[index * batch_size: (index + 1) * batch_size]
        }
    )

    output_size = theano.function(
        [index],
        [layer0.output.shape, layer1_input.shape, layer1.output.shape],
        givens={
            x: test_set_x[index * batch_size: (index + 1) * batch_size]
        }
    )

    output_model = theano.function(
        [index],
        [layer2.y_pred],
        givens={
            x: valid_set_x[index * batch_size: (index + 1) * batch_size]
        }
    )

    output_test = theano.function(
        [index],
        [layer2.y_pred],
        givens={
            x: test_set_x[index * batch_size: (index + 1) * batch_size]
        }
    )

    output_test2 = theano.function(
        [index],
        [layer0.output, layer1_input],
        #[layer1_input],
        givens={
            x: test_set_x[index * batch_size: (index + 1) * batch_size]
        }
    )
    print output_test2(0)
    params = layer2.params + layer1.params + layer0.params

    grads = T.grad(cost, params)

    updates = [
        (param_i, param_i - learning_rate * grad_i)
        for param_i, grad_i in zip(params, grads)
    ]

    train_model = theano.function(
        [index],
        cost,
        updates=updates,
        givens={
            x: train_set_x[index * batch_size: (index + 1) * batch_size],
            y: train_set_y[index * batch_size: (index + 1) * batch_size]
        }
    )

    print '... training'
    # early-stopping parameters
    patience = 20000  # look as this many examples regardless
    patience_increase = 2  # wait this much longer when a new best is
                           # found
    improvement_threshold = 0.995  # a relative improvement of this much is
                                   # considered significant
    validation_frequency = min(n_train_batches, patience / 2)
                                  # go through this many
                                  # minibatche before checking the network
                                  # on the validation set; in this case we
                                  # check every epoch

    best_validation_loss = numpy.inf
    best_params = 0
    best_iter = 0
    test_score = 0.
    start_time = time.clock()

    epoch = 0
    done_looping = False

    while (epoch < n_epochs) and (not done_looping):
        epoch = epoch + 1
        for minibatch_index in xrange(n_train_batches):

            iter = (epoch - 1) * n_train_batches + minibatch_index

            if iter % 100 == 0:
                print 'training @ iter = ', iter
            cost_ij = train_model(minibatch_index)

            if (iter + 1) % validation_frequency == 0:

                # compute zero-one loss on validation set
                validation_losses = [validate_model(i) for i
                                     in xrange(n_valid_batches)]
                #for index in range(0, n_valid_batches):
                #    print output_model(index)
                #    print valid_set_y[index * batch_size: (index + 1) * batch_size].eval()
                this_validation_loss = numpy.mean(validation_losses)
                print('epoch %i, minibatch %i/%i, validation error %f %%' %
                      (epoch, minibatch_index + 1, n_train_batches,
                       this_validation_loss * 100.))

                # if we got the best validation score until now
                if this_validation_loss < best_validation_loss:

                    #improve patience if loss improvement is good enough
                    if this_validation_loss < best_validation_loss *  \
                       improvement_threshold:
                        patience = max(patience, iter * patience_increase)

                    # save best validation score and iteration number
                    best_validation_loss = this_validation_loss
                    best_iter = iter
                    best_params = [copy.deepcopy(layer0.params), copy.deepcopy(layer1.params), copy.deepcopy(layer2.params)]

                    # test it on the test set
                    test_losses = [
                        test_model(i)
                        for i in xrange(n_test_batches)
                    ]
                    #print params[0].eval()
                    #print (params[0].eval() == layer2.params[0].eval())
                    #print validation_losses
                    for index in range(0, n_valid_batches):
                        for i in range(0, batch_size):
                            true_i = batch_size*index+i
                            #print output_model(index)
                            print validsentence[true_i], '\t',senselist[output_model(index)[0][i]], '\t', senselist[valid_set_y[true_i].eval()]
                    #print test_losses
                    test_score = numpy.mean(test_losses)
                    for index in range(0, n_test_batches):
                        for i in range(0, batch_size):
                            true_i = batch_size*index+i
                            #print output_model(index)
                            print testsentence[true_i], '\t',senselist[output_test(index)[0][i]], '\t', senselist[test_set_y[true_i].eval()]
                    print(('     epoch %i, minibatch %i/%i, test error of '
                           'best model %f %%') %
                          (epoch, minibatch_index + 1, n_train_batches,
                           test_score * 100.))

            if patience <= iter:
                done_looping = True
                break

    end_time = time.clock()
    print('Optimization complete.')
    for index in range(0, n_test_batches):
        for i in range(0, batch_size):
            true_i = batch_size*index+i
            #print output_model(index)
            print testsentence[true_i], '\t',senselist[output_test(index)[0][i]], '\t', senselist[test_set_y[true_i].eval()]
    layer0.W = copy.deepcopy(best_params[0][0])
    layer0.b = copy.deepcopy(best_params[0][1])
    #layer0.params = [layer0.W, layer0.b]
    layer1.W = copy.deepcopy(best_params[1][0])
    layer1.b = copy.deepcopy(best_params[1][1])
    #layer1.params = [layer1.W, layer1.b]
    layer2.W = copy.deepcopy(best_params[2][0])
    layer2.b = copy.deepcopy(best_params[2][1])
    #layer2.params = [layer2.W, layer2.b]
    #print output_test2(0)
    '''
    for index in range(0, n_test_batches):
        for i in range(0, batch_size):
            true_i = batch_size*index+i
            #print output_model(index)
            print testsentence[true_i], '\t',senselist[output_test(index)[0][i]], '\t', senselist[test_set_y[true_i].eval()]
    '''
    print('Best validation score of %f %% obtained at iteration %i, '
          'with test performance %f %%' %
          (best_validation_loss * 100., best_iter + 1, test_score * 100.))
    print >> sys.stderr, ('The code for file ' +
                          os.path.split(__file__)[1] +
                          ' ran for %.2fm' % ((end_time - start_time) / 60.))

if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='traincnn')
    parser.add_argument('-w', '--window_radius', action="store",dest="window_radius", type=int,default=3)
    parser.add_argument('-fh', '--filter_height', action="store",dest="filter_height", type=int,default=3)
    parser.add_argument('-fw', '--filter_width', action="store",dest="filter_width", type=int,default=1)
    parser.add_argument('-ph', '--pool_height', action="store",dest="pool_height", type=int,default=1)
    parser.add_argument('-pw', '--pool_width', action="store",dest="pool_width", type=int,default=1)
    parser.add_argument('-b', '--batch_size', action="store",dest="batch_size", type=int,default=1)
    parser.add_argument('-nk', '--nkerns', action="store",dest="nkerns", type=int,default=1)
    parser.add_argument('-n', '--n_epochs', action="store",dest="n_epochs", type=int,default=500)
    parser.add_argument('-ln', '--loginput_num', action="store",dest="loginput_num", type=int,default=50)
    parser.add_argument('-l', '--learning_rate', action="store",dest="learning_rate", type=float,default=0.1)
    parser.add_argument('-v', '--vector_size', action="store", dest="vector_size",type=int,default=50)
    parser.add_argument('-nor', '--normalized', action="store_true", dest="normalized")
    parser.add_argument('keyword')
    args = parser.parse_args()
    window_radius = args.window_radius
    learning_rate = args.learning_rate
    nkerns = args.nkerns
    n_epochs = args.n_epochs
    batch_size = args.batch_size
    filter_height = args.filter_height
    filter_width = args.filter_width
    pool_width = args.pool_width
    pool_height = args.pool_height
    loginput_num = args.loginput_num
    vector_size = args.vector_size
    normalized = args.normalized
    trainword(args.keyword.decode('utf-8'), window_radius, learning_rate, n_epochs, batch_size,nkerns, filter_height,filter_width,pool_height,pool_width,loginput_num, vector_size,normalized)
