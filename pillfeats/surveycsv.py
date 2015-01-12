#!/usr/bin/python

import csv
import datetime
import time
import json
import sys
import numpy


#Timestamp, (of when the survey was received)
#Username,
#Date for Night of Sleep,
#Time you get into bed ,
#Approximate Sleep Time,
#Approximate Wake-Up Time,
#Rate your sleep,
#"If you got up in the middle of the night, please provide the approximate time",
#Steps taken,
#"If you work-out during the day, what is the intensity level?"

survey_email_map = {'amanda@sayhello.com': 'amanda@amanda.com',
 'benjo@sayhello.com': 'benejoseph@gmail.com',
 'bryan@sayhello.com': 'bryan+a5@sayhello.com',
 'delisa@sayhello.com': 'delisa+mq@sayhello.com',
 'jimmy@sayhello.com': 'jimmy+beta2@sayhello.com',
 'kevin@sayhello.com': 'kevin+13@sayhello.com',
 'kingshy@sayhello.com': 'kingshy+35@sayhello.com',
 'km@sayhello.com': 'km+00@sayhello.com',
 'mikael@sayhello.com': 'mikael3@sayhello.com',
 'pang@sayhello.com': 'pang02@sayhello.com',
 'quino@sayhello.com': 'quino+25@sayhello.com',
 'rsb@sayhello.com': 'sparky4@sayhello.com',
 'tim@sayhello.com': 'tim@home'}
 
date_time_format = '%m/%d/%Y %I:%M:%S %p'

#sort by the first column
def sort_survey_data(survey_data):
    for key in survey_data.keys():
        
        lists = survey_data[key]

        list1 = lists[0]
        
        indexes = range(len(list1))
        indexes.sort(key=list1.__getitem__)

        for i in xrange(len(lists)):
            sorted_list = map(lists[i].__getitem__, indexes)
            lists[i] = sorted_list
    

def read_survey_data(filename, min_unix_time = 0):
    
    mydict = {}
    
    with open(filename, 'rb') as csvfile:
        reader = csv.reader(csvfile, delimiter=',')
        first = True
        for row in reader:
            if first:
                first = False 
                continue
            
            email = row[1]
            
            if email in survey_email_map:
                #print 'replacing %s for %s' % (email, survey_email_map[email])
                email = survey_email_map[email]
            
            day = row[2]
        
            time_in_bed = '%s %s' % (day, row[3])
            time_asleep = '%s %s' % (day, row[4])
            time_wake = '%s %s' % (day, row[5])
            
            
            
            times = [time_in_bed, time_asleep, time_wake]
                        
            account_id = email
            
           
            unix_times = []
            offset = 0.0
            for t in times:
                dtobj = datetime.datetime.strptime(t, date_time_format)
                
                #need to add offset???
                unix_times.append(time.mktime(dtobj.timetuple()))
                
            for i in xrange(len(unix_times)):
                unix_times[i] += offset
           
           
            #since these are all the same day, waking up at 8am is the next day...
            if 'AM' in time_in_bed:
                unix_times[0] += 86400
                
            if 'AM' in time_asleep:
                unix_times[1] += 86400
                
            if 'AM' in time_wake:
                unix_times[2] += 86400

            if min_unix_time is not None and unix_times[0] < min_unix_time:
                continue

            
            #create empty list of lists
            if not mydict.has_key(account_id):
                mydict[account_id] = [[], [], []]
            
            
            for i in xrange(len(unix_times)):
                mydict[account_id][i].append(unix_times[i])
            
           
            
            
    sort_survey_data(mydict)
            
    return mydict

if __name__ == '__main__':
    filename = sys.argv[1]

    print ('opening %s' % filename)
    survey_dict = read_survey_data(filename)
    
    foo = survey_dict['benejoseph@gmail.com']
    foo = numpy.array(foo)
    foo = foo - numpy.tile(foo[0], (3, 1))
    foo = foo / 3600
    print foo
    
    
    
    
