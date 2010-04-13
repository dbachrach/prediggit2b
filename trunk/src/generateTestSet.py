#!/usr/bin/env python3
'''
Created on 15/mar/2010

@author: ChrisN

usage: python3 generateTestSet.py startdate enddate featureDatabase pathToResultDatabase

where
startdate is of the form YYYY-M-D
enddate is of the form YYYY-M-D
featureDatabse is the relative path to the database of features
limit is the number of popular stories you want to extract (and matching number of unpopular)
pathToResultDatabase is a relative path to where you want to resulting test set database to be located

script pulls from the first second of startdate up to but not including the first second of enddate
'''

if __name__ == '__main__':

    import FeatureUtils
    import sys
    import datetime
    import calendar
          
    args = sys.argv[1:]
    
    print("Test Set: "+args[0]+" to "+args[1])
    
    startdate = args[0].split("-")
    startdate = datetime.datetime(int(startdate[0]), int(startdate[1]), int(startdate[2]))
    enddate = args[1].split("-")
    enddate = datetime.datetime(int(enddate[0]), int(enddate[1]), int(enddate[2]))
    trainingdatabasename = args[2]
    resdatabase = args[3]
    
    startstamp = calendar.timegm(startdate.utctimetuple())
    endstamp = calendar.timegm(enddate.utctimetuple())
    
    db = FeatureUtils.connectExisting("../digg.db")
    db.text_factory = bytes
    cursor = db.cursor()
    
    traindb = FeatureUtils.connectExisting(trainingdatabasename)
    traincursor = traindb.cursor()
    
    resdb = FeatureUtils.connect(resdatabase)
    rescursor = resdb.cursor()
    
    print("Executing story retrieval query...")
    
    '''execute story retrieval query for all stories between the dates supplied as arguments''' 
    cursor.execute("select * from stories where (submit_date >= ? and submit_date < ?);", (startstamp,endstamp))
    story = cursor.fetchone()
    
    traincursor.execute("select * from headline_words;")
    headlineTopWords = traincursor.fetchall()
    traincursor.execute("select * from description_words;")
    descriptionTopWords = traincursor.fetchall()
    
    wordOffset = FeatureUtils.wordOffset
    
    featuresRecord = []
    
    skippedrecords = 0
    
    print("extracting features...\n")
    
    '''extracts id, time of day, attention words, user percentage, domain percentage, topic percentage, prepares headlines and descriptions'''
    while story != None:
        
        try:
        
            '''indices are 
            id, time of day, attention word, 
            user percentage (sequential), domain percentage (sequential), topic percentage (sequential), 
            popular headline nouns count, popular description nouns count, is popular'''
            feature = [0] * 207
        
            '''pull id'''
            feature[0] = int(story[0])
        
            '''pull time of day'''
            feature[1] = FeatureUtils.extractTime(int(story[3]))
            
            '''pull attention grabbing word'''
            cleanHeadline = FeatureUtils.cleanString(str(story[1],encoding='utf8'))
            feature[2] = FeatureUtils.extractHotWord(cleanHeadline)
            
            cleanDescription = FeatureUtils.cleanString(str(story[2],encoding='utf8'))
            
            '''pull user, domain, and topic'''
            user = str(story[5],encoding='utf8').strip()
            domain = FeatureUtils.extractDomain(str(story[8],encoding='utf8'))
            topic = str(story[6],encoding='utf8').lower().strip()
        
            
            '''get weighted averages for story from database'''
            traincursor.execute("select weight from user_weights where user=?;",(user,))
            userres = traincursor.fetchall()
            
            if len(userres) == 0:
                feature[3] = 0
            elif len(userres) != 1:
                sys.exit("More than one matching user "+user+" encountered, feature database is corrupt.\nExiting...")
            else:
                feature[3] = int(userres[0][0])
                
            traincursor.execute("select weight from domain_weights where domain = ?;",(domain,))
            domainres = traincursor.fetchall()
            
            if len(domainres) == 0:
                feature[4] = 0
            elif len(domainres) != 1:
                sys.exit("More than one matching domain for "+domain+" encountered, feature database is corrupt.\nExiting...")
            else:
                feature[4] = int(domainres[0][0])
                
            traincursor.execute("select weight from topic_weights where topic = ?;",(topic,))
            topicres = traincursor.fetchall()
            
            if len(topicres) == 0:
                feature[5] = 0
            elif len(topicres) != 1:
                sys.exit("More than one matching topic "+topic+" encountered, feature database is corrupt.\nExiting...")
            else:
                feature[5] = int(topicres[0][0])
                
            i = wordOffset
            for word in headlineTopWords:
                if word[0] in cleanHeadline.lower():
                    feature[i] = 1
                    
                i += 1
                
            for word in descriptionTopWords:
                if word[0] in cleanDescription.lower():
                    feature[i] = 1
                    
                i += 1
            
            '''this is included for convenience of checking the accuracy'''
            if(str(story[4],encoding='utf8') == "popular"):
                feature[206] = 1
        
            featuresRecord.append(feature)
            
        except UnicodeDecodeError as err:
            print("Non-utf8 characters encountered, skipping record with id "+str(story[0])+"...")
            skippedrecords += 1
        finally:
            story = cursor.fetchone()
            
            
    db.close()
    traindb.close()
    stories = None
                
    
    print("\ncreating table for results...")
    
    '''create tables'''
    rescursor.execute("create table testset ('id' integer primary key not null, 'time' integer not null, 'attention' integer not null, 'user' numeric not null, 'domain' double not null, 'topic' double not null, " + ", ".join(["headlineWord"+str(y)+" integer not null"  for y in range(1,101)]) + ", " +", ".join(["descriptionWord"+str(y)+" integer not null"  for y in range(1,101)]) + ", 'popular' integer not null);")

    print("writing results to database...")
    
    '''insert features'''
    valueplaceholder = "("+ ",".join(["?"]*FeatureUtils.numFeatures)+")"
    for features in featuresRecord:
        rescursor.execute("insert into testset values "+valueplaceholder+";",features)        
        
    resdb.commit()
    resdb.close()
    
    print(str(len(featuresRecord)) + " test records inserted")
    print("skipped "+str(skippedrecords) +" records")
    print("Done!\n")
    