#!/usr/bin/env python3
'''
Created on 12/mar/2010

@author: DustinB
'''

if __name__ == '__main__':

    import FeatureUtils
    import sys
          
    args = sys.argv[1:]
    
    databasename = args[0]
    output = args[1]
    
    db = FeatureUtils.connectExisting(databasename)

    cursor = db.cursor()
    cursor.execute("select * from trainingset;")
    
    f = open(output, 'w')
    
    
    for story in cursor.fetchall():
        '''indices are 
            id, time of day, attention word, 
            user percentage (sequential), domain percentage (sequential), topic percentage (sequential), 
            popular headline words count x 100, popular description words count x 100, is popular'''
        popular = story[-1]
        if popular == 0 :
            popular = -1;
        
        f.write(str(popular))
        
        i = 1
        for val in story[1:-1]:
            f.write(" "+str(i)+":"+str(val))
            i = i + 1
        
        f.write("\n")
