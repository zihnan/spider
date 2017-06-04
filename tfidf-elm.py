# coding=UTF-8
import argparse
import codecs
import json
import numpy as np
import os
import sys
from sklearn.externals import joblib
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.model_selection import cross_val_score
from sklearn_extensions.extreme_learning_machines import ELMClassifier

def split_into_term(data):
    delimiter = ['/', '?', '.', '=', '-', '_', '!',':', ';', '|', '(', ')', ',', '@', '"', "'", '[', ']',u'，', u'、', u'！', u'【', u'】', u'“', u'”', u'・', u'『', u'』', u'｜', u'‹', u'›', u'丨', u'¥']
    tf_test = []
    for t in data:
        temp = t.strip()
        for d in delimiter:
            temp = temp.replace(d, ' ')
        t2 = [i.lower() for i in temp.split(' ') if i]
        tf_test.append(t2)
    return tf_test

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Title Extraction')
    parser.add_argument('--tfidf_percent', nargs='?',type=float, help='K% highest tf-idf term', default=0.9, action='store')
    parser.add_argument('title_list_file', nargs=1,type=str, help='sample file formated by spyder.py')
    args = parser.parse_args()
    percent = int(args.tfidf_percent * 100)
    
    print args.title_list_file
    with codecs.open(args.title_list_file[0], 'r', encoding='utf-8') as f:
        title_list = f.readlines()
        phish_title_number = len(title_list)
    '''
    with codecs.open('legitimate-title-list', 'r', encoding='utf-8') as f:
        title_list += f.readlines()
        legitimate_title_number = len(title_list) - phish_title_number
    '''
    for index, t in enumerate(title_list):
        title_list[index] = t.strip().rstrip()
        
    tf_test = split_into_term(title_list)
    
    tf_set = set([j for i in tf_test for j in i])
    tf_matrix = [[0] * len(tf_set) for _ in xrange(len(tf_test))]
    
    for r, t in enumerate(tf_test):
        for c, i in enumerate(tf_set):
            if i in t:
                tf_matrix[r][c] += 1
    
    transformer = TfidfTransformer(smooth_idf=False)
    tfidf = transformer.fit_transform(tf_matrix)
    tfidf_array = tfidf.toarray()
    
    
    """
    fltr = []
    for j in range(0, 100, 10):
         temp=[]
         for i in xrange(len(tf_matrix[0])):
             if any([k >= float(j)/float(100) for k in tfidf_array[:][i]]):
                 temp.append(i)
         fltr.append(temp)
         print len(temp)
         if os.path.exists('tfidf {}% term'.format(str(j))):
            sys.stderr.write('tfidf {}% term existed\n'.format(str(j)))
            sys.exit(0)
         with codecs.open('tfidf {}% term'.format(str(j)), 'a', encoding='utf-8') as f:
            f.write(str(temp) + '\n')
            f.write(' '.join([list(tf_set)[i] for i in temp]))
            """
            
    # >>>>>>>>>>>>>>>>>>>>>
    temp = []
    for i in xrange(len(tf_matrix[0])):
        if any([k >= percent/float(100) for k in tfidf_array[:][i]]):
            temp.append(i)
    print len(temp)
    if os.path.exists('tfidf {}% term'.format(str(percent))):
       sys.stderr.write('tfidf {}% term existed\n'.format(str(percent)))
       sys.exit(0)
    with codecs.open('tfidf {}% term'.format(str(percent)), 'a', encoding='utf-8') as f:
       f.write(str(temp) + '\n')
       f.write(' '.join([list(tf_set)[i] for i in temp]))
           
    # >>>>>>>>>>>>>>>>>>>>>
            
    with codecs.open('tfidf {}% term'.format(str(percent)), 'r', encoding='utf-8') as f:
        f.readline()
        tfidf_list = f.readline().rstrip().split(' ')
        tfidf_dict = {}
        for t in tfidf_list:
            if t.lower() not in tfidf_dict:
                tfidf_dict[t.lower()] = 1
            else:
                tfidf_dict[t.lower()] += 1
                
    assert len(tfidf_dict) == len(tfidf_list)
    for term1, term2 in zip(tfidf_dict,tfidf_list):
        print term1,term2
        
    with open('tfidf {}% term'.format(str(percent)), 'r') as f:
        temp = f.readline()
        top_list = json.loads(temp.rstrip())
        
    sys.stderr.write('Initializing feature matrix ... \n')
    elm_train_matrix = [[0] * len(top_list) for _ in xrange(len(tfidf_array))]
    cls_train_matrix = [0] * len(tfidf_array)
    sys.stderr.write('Converting sample data to feature matrix ... \n')
    for index1, i in enumerate(tfidf_array):
        for index2, j in enumerate(top_list):
            if i[j] >= percent / float(100):
                elm_train_matrix[index1][index2] = 1
                cls_train_matrix[index1] = 1
    sys.stderr.write('Initializing ELM Classifier ...\n')
    clf = ELMClassifier(activation_func='sigmoid') # default activation function is tanh
    
    sys.stderr.write('Training ELM Classifier ... \n')
    clf = clf.fit(np.array(elm_train_matrix), np.array(cls_train_matrix))
    score = cross_val_score(clf, np.array(elm_train_matrix), np.array(cls_train_matrix), scoring='f1')
    print '{}% TF-IDF:'.format(str(percent))
    print '\tMean\t: {:.2f}%'.format(score.mean()*100)
    print '\tStd\t: {:.2f}%'.format(score.std()*100)
    sys.stderr.write('Saving ELM Model ... \n')
    joblib.dump(clf, 'tfidf-{}%-elm.model'.format(str(percent)))
    
    """
    for percent in range(0, 100, 10):
        if percent > 10:
            continue
        sys.stderr.write('Loading sample data ... \n')
        with open('tfidf2 {}% term'.format(str(percent)), 'r') as f:
            temp = f.readline()
            top_list = json.loads(temp.rstrip())
            
        sys.stderr.write('Initializing feature matrix ... \n')
        elm_train_matrix = [[0] * len(top_list) for _ in xrange(len(tfidf_array))]
        cls_train_matrix = [0] * len(tfidf_array)
        '''
        elm_train_matrix = [[0] * len(top_list) for _ in xrange(len(tfidf_array) * 9 / 10)]
        cls_train_matrix = [0] * (len(tfidf_array) * 9 / 10)
        elm_test_matrix = [[0] * len(top_list) for _ in xrange(len(tfidf_array) / 10)]
        cls_test_matrix = [0] * (len(tfidf_array) / 10)
        '''
        sys.stderr.write('Converting sample data to feature matrix ... \n')
        for index1, i in enumerate(tfidf_array):
            for index2, j in enumerate(top_list):
                if i[j] >= percent / float(100):
                    elm_train_matrix[index1][index2] = 1
                    cls_train_matrix[index1] = 1
            '''
            if index1 < len(tfidf_array) * 9 / 10:
                for index2, j in enumerate(top_list):
                    if tfidf_array[index1][j] >= 0.9:
                        elm_train_matrix[index1][index2] = 1
                        cls_train_matrix[index1] = 1
            else:
                for index2, j in enumerate(top_list):
                    if tfidf_array[index1][j] >= 0.9:
                        elm_test_matrix[index1 - len(tfidf_array) * 9 / 10][index2] = 1
                        cls_test_matrix[index1 - len(tfidf_array) * 9 / 10] = 1
                    
        temp = np.array(elm_train_matrix)
        for index, i in enumerate(temp):
            if np.isnan(i).any():
                print 'isnan ', index, i
            if np.isinf(i).any():
                print 'isinf ', index, i
        '''
        sys.stderr.write('Initializing ELM Classifier ...\n')
        clf = ELMClassifier() # default activation function is tanh
        
        sys.stderr.write('Training ELM Classifier ... \n')
        clf = clf.fit(np.array(elm_train_matrix), np.array(cls_train_matrix))
        score = cross_val_score(clf, np.array(elm_train_matrix), np.array(cls_train_matrix), scoring='f1')
        print '{}% TF-IDF:'.format(str(percent))
        print '\tMean\t: {:.2f}%'.format(score.mean()*100)
        print '\tStd\t: {:.2f}%'.format(score.std()*100)
        sys.stderr.write('Saving ELM Model ... \n')
        joblib.dump(clf, 'tfidf-{}%-elm.model'.format(str(percent)))
        """
