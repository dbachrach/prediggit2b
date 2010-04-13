#!/usr/bin/env python3
'''
Created on 12/mar/2010

@author: ChrisN

usage: python3 extractor.py startdate enddate pathToResultDatabase

where
startdate is of the form YYYY-M-D
enddate is of the form YYYY-M-D
pathToResultDatabase is a relative path to where you want to resulting test set database to be located

script pulls from the first second of startdate up to but not including the first second of enddate
'''


def emptyPair():
    return [0,0]

if __name__ == '__main__':

    import FeatureUtils
    import sys
    import collections
    import datetime
    import calendar
    from tfidf import TfIdf
    from operator import itemgetter
          
    args = sys.argv[1:]
    
    print("Features for "+args[0]+" to "+args[1])
    
    startdate = args[0].split("-")
    startdate = datetime.datetime(int(startdate[0]), int(startdate[1]), int(startdate[2]))
    enddate = args[1].split("-")
    enddate = datetime.datetime(int(enddate[0]), int(enddate[1]), int(enddate[2]))
    databasename = args[2]
    
    resdb = FeatureUtils.connect(databasename)
    
    rescursor = resdb.cursor()
    
    db = FeatureUtils.connectExisting("../digg.db")
    db.text_factory = bytes
    
    print("Executing story retrieval query...")
    
    '''execute story retrieval query for all stories between the dates supplied as arguments''' 
    cursor = db.cursor()
    cursor.execute("select * from stories where (submit_date >= ? and submit_date < ?) order by submit_date asc;", (calendar.timegm(startdate.utctimetuple()), calendar.timegm(enddate.utctimetuple())))
    
    domains = collections.defaultdict(emptyPair)
    users = collections.defaultdict(emptyPair)
    topics = collections.defaultdict(emptyPair)
    headlineBuffer = []
    descriptionBuffer = []
    headlineWeigher = TfIdf()
    descriptionWeigher = TfIdf()
    
    featuresRecord = []
    
    story = cursor.fetchone()
    
    skippedrecords = 0
    numfeatures = FeatureUtils.numFeatures
    wordOffset = FeatureUtils.wordOffset
    
    print("extracting initial features...\n")
    
    '''extracts id, time of day, attention words, user percentage, domain percentage, topic percentage, prepares headlines and descriptions'''
    while story != None:
        
        try:
        
            '''indices are 
            id, time of day, attention word, 
            user percentage (sequential), domain percentage (sequential), topic percentage (sequential), 
            popular headline words count x 100, popular description words count x 100, is popular'''
            feature = {}
        
            '''pull id'''
            feature[0] = int(story[0])
        
            '''pull time of day'''
            feature[1] = FeatureUtils.extractTime(int(story[3]))
        
            '''pull attention grabbing word'''
            cleanHeadline = FeatureUtils.cleanString(str(story[1],encoding='utf8'))
            feature[2] = FeatureUtils.extractHotWord(cleanHeadline)
        
            user = str(story[5],encoding='utf8').strip()
            domain = FeatureUtils.extractDomain(str(story[8],encoding='utf8'))
            topic = str(story[6],encoding='utf8').lower().strip()
        
            users[user][1] += 1
            domains[domain][1] += 1
            topics[topic][1] += 1
            
            cleanDescription = FeatureUtils.cleanString(str(story[2],encoding='utf8'))
        
            if(str(story[4],encoding='utf8') == "popular"):
                users[user][0] += 1
                domains[domain][0] += 1
                topics[topic][0] += 1
                feature[numfeatures-1] = 1
                headlineBuffer.append(cleanHeadline)
                descriptionBuffer.append(cleanDescription)
            
            '''compute weighted averages for stories so far'''
            feature[3] = users[user][0] * users[user][0] / users[user][1]
            feature[4] = domains[domain][0] * domains[domain][0] / domains[domain][1]
            feature[5] = topics[topic][0] * topics[topic][0] / topics[topic][1]
            
            feature[6] = cleanHeadline
            feature[7] = cleanDescription
            
            headlineWeigher.add_input_document(cleanHeadline)
            descriptionWeigher.add_input_document(cleanDescription)

            featuresRecord.append(feature)
            
        except UnicodeDecodeError as err:
            print("Non-utf8 characters encountered, skipping record with id "+str(story[0])+"...")
            skippedrecords += 1
            
        finally:
            story = cursor.fetchone()
        
    db.close()
    
    print("\nextracting top headline and description words...")
    
    
    '''get top words based on TfIdf rankings for each headline and description'''
    topHeadlineWords = {} 
    topDescriptionWords = {} 
    
    for headline in headlineBuffer:
        restfidf = headlineWeigher.get_doc_keywords(headline)
        
        for pair in restfidf:
            if pair[0] in topHeadlineWords:
                topHeadlineWords[pair[0]] *= pair[1]
            else:
                topHeadlineWords[pair[0]] = pair[1]
            
            
    for description in descriptionBuffer:
        restfidf = descriptionWeigher.get_doc_keywords(description)
        
        for pair in restfidf:
            if pair[0] in topDescriptionWords:
                topDescriptionWords[pair[0]] *= pair[1]
            else:
                topDescriptionWords[pair[0]] = pair[1]

    
    topHeadlineWords = sorted(topHeadlineWords.items(), key=itemgetter(1), reverse=True)
    topDescriptionWords = sorted(topDescriptionWords.items(), key=itemgetter(1), reverse=True)
    
    topHeadlineWords,x = zip(*topHeadlineWords)
    topDescriptionWords,x = zip(*topDescriptionWords)
    x=None
    
    topHeadlineWords = list(topHeadlineWords)[0:100]
    topDescriptionWords = list(topDescriptionWords)[0:100]
    
#    print(topHeadlineWords)
#    print(topDescriptionWords)
#    sys.exit(0)
    
    '''add binary flag if word appears in the headline or description'''
    for feature in featuresRecord:
        
        i = wordOffset
        hline = feature[6].lower()
        dline = feature[7].lower()
        
        feature[6] = 0
        feature[7] = 0
        
        for word in topHeadlineWords:
            
            if word in hline:
                feature[i] = 1
                
            i += 1
                
        for word in topDescriptionWords:
            
            if word in dline:
                feature[i] = 1
                
            i += 1

                
    
    print("creating tables for results...")
    
    '''create tables'''
    rescursor.execute("create table features ('id' integer primary key not null, 'time' integer not null, 'attention' integer not null, 'user' numeric not null, 'domain' double not null, 'topic' double not null, " + ", ".join(["headlineWord"+str(y)+" integer not null"  for y in range(1,101)]) +", " + ", ".join(["descriptionWord"+str(y)+" integer not null"  for y in range(1,101)]) + ", 'popular' integer not null);")
    rescursor.execute("create table headline_words('word' text not null primary key);")
    rescursor.execute("create table description_words('word' text not null primary key);")
    rescursor.execute("create table user_weights('user' text not null primary key, 'weight' double not null);")
    rescursor.execute("create table domain_weights('domain' text not null primary key, 'weight' double not null);")
    rescursor.execute("create table topic_weights('topic' text not null primary key, 'weight' double not null);")
    
    print("writing results to database...")
    
    '''insert features'''
    fields = ["?"]*numfeatures
    fieldsstring = "("+",".join(fields)+")"
    for features in featuresRecord:
        i = 0
        fs = [0] * FeatureUtils.numFeatures
        
        while i < FeatureUtils.numFeatures:
            if i in features.keys():
                fs[i] = features[i]
                
            i += 1
                
        rescursor.execute("insert into features values "+fieldsstring+";",fs)
        
    '''insert top headline words'''
    for word in topHeadlineWords:
        rescursor.execute("insert into headline_words values (?);",(word,))
        
    '''insert top description words'''
    for word in topDescriptionWords:
        rescursor.execute("insert into description_words values (?);",(word,))
                
    '''insert user and weight in user_weights table'''
    
    for user in users.keys():
        rescursor.execute("insert into user_weights (user,weight) values (?,?);",(user,users[user][0] * users[user][0] / users[user][1]))
        
    '''insert domain and weight in domain_weights table'''
    for domain in domains.keys():
        rescursor.execute("insert into domain_weights (domain,weight) values (?,?);",(domain,domains[domain][0] * domains[domain][0] / domains[domain][1]))
        
    '''insert topic and weight in topic_weights table'''
    for topic in topics.keys():
        rescursor.execute("insert into topic_weights (topic,weight) values (?,?);",(topic,topics[topic][0] * topics[topic][0] / topics[topic][1]))
        
        
    resdb.commit()
    resdb.close()
    
    print(str(len(featuresRecord)) + " feature records inserted")
    print("skipped "+str(skippedrecords) +" records")
    print("Done!\n")
    
    
    