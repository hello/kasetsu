#!/usr/bin/python
import csv
import datetime
import time
import json

#0: ambient_temp
#1: ambient_humidity
#2: ambient_light
#3: local_utc_ts
#4: account_id
#5: device_id
#6: email


def sort_sense_data(sense_data):
    for key in sense_data.keys():
            for device in sense_data[key]:
                
                lists = sense_data[key][device]
                list1 = lists[0] #sort on first list

                indexes = range(len(list1))
                indexes.sort(key=list1.__getitem__)
                
                for k in range(len(lists)):
                    this_list = lists[k]
                    sorted_list = map(this_list.__getitem__, indexes)
                    lists[k] = sorted_list


                

def read_sense_csv(filename, min_unix_time):
    iter = 0
    
    mydict = {}
    
    with open(filename, 'rb') as csvfile:
        reader = csv.reader(csvfile, delimiter=',')
        first = True
        for row in reader:
            if first:
                first = False 
                continue
            
            device_id = row[5]
            #account_id = row[4]
            temperature = int(row[0])
            humdity = int(row[1])
            light = int(row[2])
            email = row[6]
            account_id = email
            
            datestr = row[3]
         
            
            #2014-05-12 21:02:00
            try:
                if '.' in datestr:
                    mystrs = datestr.split('.')
                    thetime = datetime.datetime.strptime(mystrs[0], '%Y-%m-%d %H:%M:%S')
                else:
                    thetime = datetime.datetime.strptime(datestr, '%Y-%m-%d %H:%M:%S')
                timevalue = time.mktime(thetime.timetuple())
            except Exception:
                print 'error parsing %s for time' % datestr
                continue

            if min_unix_time is not None and timevalue < min_unix_time:
                continue

            if not mydict.has_key(account_id):
                mydict[account_id] = {}
                
            if not mydict[account_id].has_key(device_id):
                mydict[account_id][device_id] = [[], [], [], []]
                
            lists = mydict[account_id][device_id]; 
            lists[0].append(timevalue)
            lists[1].append(int(temperature))
            lists[2].append(int(humdity))
            lists[3].append(int(light))

            
                        
            iter = iter + 1
            
    sort_sense_data(mydict)
    
    return mydict
