#!/usr/bin/env python3
'''
Created on 12/mar/2010

@author: ChrisN
'''

from sqlite3 import dbapi2 as sqlite3
import os
import datetime
import re
import sys
import random

whitespaceregex = re.compile("\s+")
numFeatures = 207
wordOffset = 6

def connect(filename):
    filepath = None
    
    if filename[0] == "/":
        filepath = filename
    else:
        filepath = os.path.normpath(os.getcwd() + "/"+ filename)

    db = sqlite3.connect(filepath)
    return db

def connectExisting(filename):
    filepath = None
    
    if filename[0] == "/":
        filepath = filename
    else:
        filepath = os.path.normpath(os.getcwd() + "/"+ filename)
    
    if os.path.exists(filepath):
        db = sqlite3.connect(filepath)
        return db
    else:
        sys.exit("Unable to connect to database: "+filepath+"\nExiting...")
        
def extractDomain(url):
    domain = url.strip().lower()
    domain = domain.lstrip("http://")
    
    index = domain.find("/")
    
    if index != -1:
        domain = domain[0:index]
    
    return domain

def extractTime(timestamp):
    return int(datetime.datetime.fromtimestamp(timestamp).strftime("%H%M%S"))

def cleanString(astring):
    cleanstring = astring.strip()
    cleanstring = whitespaceregex.sub(" ", cleanstring)
    return cleanstring

def extractHotWord(headline):
    stub = headline.lower()
    
    if stub.startswith("breaking"):
        return 1
    
    if stub.startswith("exclusive"):
        return 2
    
    if stub.startswith("unveild"):
        return 3
    
    if stub.startswith("top "):
        return 4
    
    if stub.startswith("urgent"):
        return 5
    
    if stub.startswith("never before"):
        return 6
    
    return 0

def insertNounCountPair(pair, list):
    i = 0;
    
    while i < len(list):
        if not list[i][1] > pair[1]:
            list.insert(i, pair)
            break
        
        i += 1 

def extractTopWords(wordsDict, count):
    if len(wordsDict.keys()) <= count:
        return dict(**wordsDict)
    
    topWords = []
    
    for noun in wordsDict.keys():
        if len(topWords) >= count:
            topWords.pop()
            
        insertNounCountPair((noun, wordsDict[noun]), topWords)
        
        
    return dict(topWords)

def getTestSet(popular,unpopular,limit):
    if len(popular) == limit and len(unpopular) == limit:
        res = list(popular)
        res.extend(unpopular)
        res.shuffle(popular)
        return res
    
    lowerlimit = limit
    
    if len(unpopular) < lowerlimit:
        lowerlimit = len(unpopular)
        
    if len(popular) < lowerlimit:
        lowerlimit = len(popular)
        
    unpop = random.sample(unpopular, lowerlimit)
    pop = random.sample(popular, lowerlimit)
   
    pop.extend(unpop)
    random.shuffle(pop)
    return pop
