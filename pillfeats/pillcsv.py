#!/usr/bin/python
import csv
import datetime
import time
import json

def sort_pill_data(pill_data):
    for key in pill_data.keys():
        lists = pill_data[key]
        
        list1 = lists[0]
        list2 = lists[1]
        
        indexes = range(len(list1))
        indexes.sort(key=list1.__getitem__)

        sorted_list1 = map(list1.__getitem__, indexes)
        sorted_list2 = map(list2.__getitem__, indexes)
        
        lists[0] = sorted_list1
        lists[1] = sorted_list2

def read_pill_csv(filename, min_unix_time):
    iter = 0
    
    mydict = {}
    
    with open(filename, 'rb') as csvfile:
        reader = csv.reader(csvfile, delimiter=',')
        first = True
        for row in reader:
            if first:
                first = False 
                continue
            
            pill_id = row[2]
            value = int(row[3])
            datestr = row[6]
            
            if value < 0:
                continue
            
            
            #2014-05-12 21:02:00
            thetime = datetime.datetime.strptime(datestr, '%Y-%m-%d %H:%M:%S')
            timevalue = time.mktime(thetime.timetuple())

            if min_unix_time is not None and timevalue < min_unix_time:
                continue

            if not mydict.has_key(pill_id):
                mydict[pill_id] = [[], []]
                
            lists = mydict[pill_id]; 
            lists[0].append(timevalue)
            lists[1].append(int(value))
            
                        
            iter = iter + 1
            
    return mydict
