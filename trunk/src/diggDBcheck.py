#!/usr/bin/env python3
'''
Created on 12/mar/2010

@author: DustinB
'''


def emptyPair():
    return [0,0]

if __name__ == '__main__':

    import FeatureUtils
    import sys
    import collections
    from datetime import datetime
    import calendar
    from operator import itemgetter
    
    db = FeatureUtils.connectExisting('/Users/deb/repositories/prediggit2b/digg.db')

    cursor = db.cursor()
    cursor.execute("select submit_date from stories ORDER BY submit_date")
    
    
    dates = {}
    
    for story in cursor.fetchall() :
  
        s_date = story[0]
        
        dt = datetime.fromtimestamp(s_date).strftime("%m/%d/%Y")
        if dt in dates :
            dates[dt] += 1
        else :
            dates[dt] = 1
            
            
    dates = sorted(dates.items(), key=itemgetter(0))
    
    for date in dates :
        print(date)
    
    
        
        
            
                     