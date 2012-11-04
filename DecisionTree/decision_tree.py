#!/usr/local/bin/python
# -*- coding : utf-8 -*-

import sys
import os
import math

"""
Author : zengkui
Created Time : Sun 03 Nov 2012 10:12:47 PM CST
FileName : decision_tree.py
Description : text classifier 
ChangeLog : 
"""

did2label = {}
wid2word = {}
didwordlist = {} 
widdoclist = {}

def load():
    fp = open( "./doc2word_index" )
    a,b,c = fp.readline().strip('\r\n').split('\t')
    for i in range ( 0, int(a) ):
        doc_id,word_count,label = fp.readline().strip('\r\n').split('\t')
        doc_id = int(doc_id)
        word_count = int(word_count)
        label = int(label)
        did2label[doc_id] = label
        didwordlist[doc_id] = set()
        for k in range (0, word_count ) :
            word, word_id, tf = fp.readline().strip('\r\n').split('\t')
            wid = int(word_id)
            tf = int(tf)
            wid2word[wid] = word
            didwordlist[doc_id].add(wid)
    fp.close()

    fp = open("./word2doc_index")
    n = fp.readline().strip('\r\n')
    for i in range (0, int(n) ):
        word,wid,df = fp.readline().strip('\r\n').split('\t')
        wid = int(wid)
        df = int(df)
        widdoclist[wid] = set()
        for k in range (0, df):
            doc_id,label = fp.readline().strip('\r\n').split('\t')
            doc_id = int(doc_id)
            label = int(label)
            widdoclist[wid].add(doc_id)
    fp.close()


def entropy( num, den ):
    if num == 0 :
        return 0
    p = float(num)/float(den)   
    return -p*math.log(p,2)


class DecisionTree :
    def __init__(self) :
        self.word = None
        self.doc_count = 0
        self.positive = 0
        self.negative = 0
        self.child = {}

    def predict(self, word_list ):
        if len(self.child) == 0 :
                return float(self.positive)/(self.positive+self.negative)
        if self.word in word_list :
            return self.child["left"].predict(word_list)
        else :
            return self.child["right"].predict(word_list)

    def visualize(self) :
        "visualize the tree"
        for i in range (0, d) :
            print "-",
        print "(%s,%d,%d)" % ( self.word,self.positive, self.negative)
        if len(self.child) != 0 :
            self.child["left"].visualize()
            self.child["right"].visualize()
         
    def build_dt(self, doc_list ) :
        self.doc_count = len(doc_list)
        for did in doc_list :
            if did2label[did] > 0 :
                self.positive += 1
            else :
                self.negative += 1

        if self.doc_count <= 10 or self.positive * self.negative == 0 : 
            return True            
        wid = info_gain( doc_list )
        if wid == -1 : 
            return True        
        self.word = wid2word[wid]
        left_list = set() 
        right_list = set() 
        for did in doc_list :
            if did in widdoclist[wid] :
                left_list.add(did)
            else :
                right_list.add(did)

        self.child["left"] =  DecisionTree()
        self.child["right"] =  DecisionTree()
        self.child["left"].build_dt( left_list )
        self.child["right"].build_dt(right_list )

def info_gain(doc_list):
    collect_word = set()
    total_positive = 0
    total_negative = 0
    for did in doc_list :
        for wid in didwordlist[did] :
            collect_word.add(wid)
        if did2label[did] > 0 :
            total_positive += 1
        else :
            total_negative += 1
    total = len(doc_list)
    info = entropy( total_positive, total )
    info += entropy( total_negative, total )
    ig = []
    for wid in collect_word :
        positive = 0
        negative = 0
        for did in widdoclist[wid]:
            if did not in doc_list :
                continue
            if did2label[did] > 0 :
                positive += 1
            else :
                negative += 1
        df = negative + positive 
        a = info
        b = entropy( positive, df )     
        b += entropy( negative, df )     
        a -= b * df / total

        b = entropy( total_positive - positive, total - df)     
        b += entropy( total_negative - negative, total - df )     
        a -= b * ( total - df ) / total
        a = a * 100000.0
        ig.append( (a, wid))
    ig.sort()
    ig.reverse()
    for i,wid in ig :
        left = 0
        right = 0
        for did in doc_list :
            if did in widdoclist[wid] :
                left += 1
            else :
                right += 1
        if left >= 5 and right >= 5 :
            return wid
    return -1 




if __name__ == "__main__" :

    load()
    dt = DecisionTree()
    doc_list = set() 
    for did in did2label :
        doc_list.add(did)
    dt.build_dt(doc_list)
    fp = open("data.test")
    true_positive = 0
    false_positive = 0
    positive = 0
    true_negative = 0
    false_negative = 0
    negative = 0
    total = 0
    while True :
        line = fp.readline()
        if len( line ) <= 0 :
            break
        arr = line.strip('\r\n').split('\t')
        label = int(arr[0])
        word_list = set() 
        for w in arr[1:] :
            if len(w) <= 3 :
                continue
            word_list.add( w )
        p = dt.predict(word_list)
        print label, p
        if label == 1 :
            positive += 1
        else :
            negative += 1
        if p == 1 :
            if label == 1 : 
                true_positive += 1
            else :
                false_positive += 1
        else :
            negative += 1
            if label == -1 :
                true_negative += 1
            else :
                false_negative += 1
        total += 1
    print "Positive recall :%f" % (true_positive*100.0/(positive))
    print "Positive precision :%f" % (true_positive*100.0/(true_positive+false_positive))
    print "Accuary : %f" % ( (true_positive + true_negative)*100.0/total)
             


