#-*- coding: utf-8 -*-
import os
import sys
import time

import numpy

import theano
import theano.tensor as T
from theano.tensor.signal import downsample
from theano.tensor.nnet import conv

from logistic_sgd import LogisticRegression
from mlp import HiddenLayer
from convolution import WsdConvPoolLayer
from setting import *
from datafetch import *

from pymongo import MongoClient
client = MongoClient()

db = client.wsd
dictdb = db.dict

def load_data_random():
    featurenum = 350
    input = open('randomdata.txt','rb')
    data = input.read().split('\n')
    del data[len(data)-1]

    trainnumpydata_x = []
    trainnumpydata_y = []
    for i in data[0:int(len(data)*0.6)]:
    	dataarray = i.split(',')
    	dataarray = [float(j) for j in dataarray]
    	#print type(dataarray[0])
    	if len(dataarray) != featurenum+1:
    		continue
        trainnumpydata_x.append(numpy.array(dataarray[0:featurenum]))
        trainnumpydata_y.append(numpy.int64(dataarray[-1]))
    train_set =  (trainnumpydata_x,trainnumpydata_y)
    
    testnumpydata_x = []
    testnumpydata_y = []
    for i in data[int(len(data)*0.6):int(len(data)*0.8)]:
    	dataarray = i.split(',')
    	if len(dataarray) != featurenum+1:
    		continue
        testnumpydata_x.append(numpy.array(dataarray[0:featurenum]))
        testnumpydata_y.append(numpy.int64(dataarray[-1]))

    test_set = (testnumpydata_x,testnumpydata_y)

    validnumpydata_x = []
    validnumpydata_y = []
    for i in data[int(len(data)*0.8):len(data)]:
    	dataarray = i.split(',')
    	if len(dataarray) != featurenum+1:
    		continue
        validnumpydata_x.append(numpy.array(dataarray[0:featurenum]))
        validnumpydata_y.append(numpy.int64(dataarray[-1]))

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

def trainword(keyword):

    rng = numpy.random.RandomState(23455)
    datasets = load_data_word(keyword)

    train_set_x, train_set_y = datasets[0]
    valid_set_x, valid_set_y = datasets[1]
    test_set_x, test_set_y = datasets[2]


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
        filter_shape=(1, 1, 3, 1),
        poolsize=(1, vector_size)
    )

    layer1_input = layer0.output.flatten(2)

    layer1 = HiddenLayer(
        rng,
        input=layer1_input,
        n_in=2*window_radius-1,
        n_out=3,
        activation=T.tanh
    )

    layer2 = LogisticRegression(input=layer1.output, n_in=3, n_out=20)

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

    output_model = theano.function(
        [index],
        [layer0.output.shape, layer1.output.shape],
        givens={
            x: test_set_x[index * batch_size: (index + 1) * batch_size]
        }
    )

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
    patience = 10000  # look as this many examples regardless
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

                    # test it on the test set
                    test_losses = [
                        test_model(i)
                        for i in xrange(n_test_batches)
                    ]
                    test_score = numpy.mean(test_losses)
                    print(('     epoch %i, minibatch %i/%i, test error of '
                           'best model %f %%') %
                          (epoch, minibatch_index + 1, n_train_batches,
                           test_score * 100.))

            if patience <= iter:
                done_looping = True
                break

    end_time = time.clock()
    print('Optimization complete.')
    print('Best validation score of %f %% obtained at iteration %i, '
          'with test performance %f %%' %
          (best_validation_loss * 100., best_iter + 1, test_score * 100.))
    print >> sys.stderr, ('The code for file ' +
                          os.path.split(__file__)[1] +
                          ' ran for %.2fm' % ((end_time - start_time) / 60.))

if __name__ == '__main__':
    trainword(u'我')