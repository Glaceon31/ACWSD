from setting import *
from datafetch import load_data_word
import argparse
import codecs
import os
import time

def crf(keyword):
    datasets = load_data_word(keyword, 3)

    train_set_x, train_set_y, trainsentence = datasets[0][0]
    valid_set_x, valid_set_y, validsentence = datasets[0][1]
    test_set_x, test_set_y, testsentence = datasets[0][2]

    senselist = datasets[1]

    content = ''
    testcontent = ''

    for i in range(0, len(trainsentence)):
        for j in range(0, len(trainsentence[i])/2):
            if trainsentence[i][j] == ' ':
                continue
            content += trainsentence[i][j]+' 0 '+'X\n'
        content +=trainsentence[i][len(trainsentence[i])/2]+' 1 '+senselist[train_set_y[i].eval()]+'\n'
        for j in range(len(trainsentence[i])/2+1, len(trainsentence[i])):
            if trainsentence[i][j] == ' ':
                continue
            content += trainsentence[i][j]+' 0 '+'X\n'
        content += '\n'
    '''
    for i in range(0, len(validsentence)):
        for j in range(0, len(validsentence[i])/2):
            if validsentence[i][j] == ' ':
                continue
            content += validsentence[i][j]+' 0 '+'X\n'
        content +=validsentence[i][len(validsentence[i])/2]+' 1 '+senselist[valid_set_y[i].eval()]+'\n'
        for j in range(len(validsentence[i])/2+1, len(validsentence[i])):
            if validsentence[i][j] == ' ':
                continue
            content += validsentence[i][j]+' 0 '+'X\n'
        content += '\n'
    '''

    for i in range(0, len(testsentence)):
        for j in range(0, len(testsentence[i])/2):
            if testsentence[i][j] == ' ':
                continue
            testcontent += testsentence[i][j]+' 0 '+'X\n'
        testcontent += testsentence[i][len(testsentence[i])/2]+' 1 '+senselist[test_set_y[i].eval()]+'\n'
        for j in range(len(testsentence[i])/2+1, len(testsentence[i])):
            if testsentence[i][j] == ' ':
                continue
            testcontent += testsentence[i][j]+' 0 '+'X\n'
        testcontent += '\n'

    output = codecs.open('crf//train//'+keyword+'_crf.txt', 'wb', 'utf-8')
    output.write(content)
    output.close()

    testoutput = codecs.open('crf//test//'+keyword+'_crf.txt', 'wb', 'utf-8')
    testoutput.write(testcontent)
    testoutput.close()

    time.sleep(1)

    os.system('crf_learn crf/template crf/train/'+keyword.encode('utf-8')+'_crf.txt crf/model/'+keyword.encode('utf-8')+'_crf')
    time.sleep(1)
    os.system('crf_test -m crf/model/'+keyword.encode('utf-8')+'_crf crf/test/'+keyword.encode('utf-8')+'_crf.txt > crf/output/'+keyword.encode('utf-8')+'_crf.txt')

    #check resuilt
    num = 0
    taggednum = 0
    predictnum = 0
    rightnum = 0
    inp = open('crf/output/'+keyword.encode('utf-8')+'_crf.txt', 'rb').read()
    words = inp.split('\n')
    print words
    for word in words:
        if word == '':
            continue
        tokens = word.split('\t')
        if tokens[0] == keyword.encode('utf-8') and tokens[1] != 'X':
            num += 1
            if tokens[2] != 'X':
                taggednum += 1
                if tokens[3] != 'X':
                    predictnum += 1
                    if tokens[2] == tokens[3]:
                        rightnum += 1

    print 'tagged: '+str(taggednum)
    print 'predict: '+str(predictnum)
    print 'right: '+str(rightnum)

    precision = 1.*rightnum/predictnum
    recall = 1.*rightnum/taggednum
    if precision+recall == 0:
        F = 0.0
    else:
        F = 2*precision*recall/(precision+recall)
    print 'precision: '+str(precision)+' recall: '+str(recall)+' F: '+str(F)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('keyword')
    args = parser.parse_args()
    crf(args.keyword.decode('utf-8'))