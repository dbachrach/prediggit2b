#!/usr/bin/env python3
'''
Created on 16/mar/2010

@author: ChrisN

usage: python generateRandomSample featureDatabase limit pathToResultDatabase

where
featureDatabse is the relative path to the database of features
limit is the number of popular stories you want to extract (and matching number of unpopular)
pathToResultDatabase is a relative path to where you want to resulting test set database to be located

if there are fewer popular stories than limit, then total number of popular stories are pulled instead
with corresponding number unpopular stories, otherwise a random subset matching limit is pulled
'''
if __name__ == '__main__':

    import FeatureUtils
    import sys
          
    args = sys.argv[1:]
    
    trainingdatabasename = args[0]
    limit = int(args[1])
    resdatabase = args[2]
    
    traindb = FeatureUtils.connectExisting(trainingdatabasename)
    traincursor = traindb.cursor()
    
    resdb = FeatureUtils.connect(resdatabase)
    rescursor = resdb.cursor()
    
    print("Executing feature records retrieval query...")
    
    '''execute story retrieval query for all stories between the dates supplied as arguments''' 
    traincursor.execute("select * from features where (popular = 1);")
    popular = traincursor.fetchall()
    
    traincursor.execute("select * from features where (popular = 0);")
    unpopular = traincursor.fetchall()
    traindb.close()
    
    print("Incorporating limiting term and extracting random subset...")
    sample = FeatureUtils.getTestSet(popular, unpopular, limit)
    
    '''release result lists for garbage collection'''
    popular = None
    unpopular = None
    
    print("creating table for results...\n")
    
    '''create tables'''
    rescursor.execute("create table trainingset ('id' integer primary key not null, 'time' integer not null, 'attention' integer not null, 'user' numeric not null, 'domain' double not null, 'topic' double not null, " + ", ".join(["headlineWord"+str(y)+" integer not null"  for y in range(1,101)]) + ", ".join(["descriptionWord"+str(y)+" integer not null"  for y in range(1,101)]) + ", 'popular' integer not null);")

    print("writing results to database...\n")
    
    '''insert sample'''
    valueplaceholder = "("+ ",".join(["?"]*207)+")"
    for instance in sample:
        rescursor.execute("insert into trainingset values " + valueplaceholder,instance)        
        
    resdb.commit()
    resdb.close()
    
    print(str(len(sample)) + " training records inserted")
    print("Done!")
    