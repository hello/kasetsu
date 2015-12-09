#!/usr/bin/python

import sys
import csv
import datetime
import calendar
dt_threshold = 30
event_map = {'IN_BED' : '11', 'SLEEP' : '12' , 'OUT_OF_BED' : '13' , 'WAKE_UP' : '14' }
event_map_reversed = dict((reversed(item) for item in event_map.items()))

event_types_str = ['SLEEP','IN_BED','WAKE_UP','OUT_OF_BED']


base_date = '1970-01-01'

def get_feedback_date_time_as_timestamp(datestr,timestr):
    datestr = datestr.split(' ')[0]
    mydate = datetime.datetime.strptime(datestr,'%Y-%m-%d')
    ts = calendar.timegm(mydate.utctimetuple())
    
    HH,MM = timestr.split(':')
    HH = int(HH)
    MM = int(MM)

    ts += HH * 3600
    ts += MM * 60

    if HH < 16:
        ts += 86400

    return ts
    

def get_feedback_datestr_as_timestamp(datestr):
    mydate = datetime.datetime.strptime(datestr, '%Y-%m-%d %H:%M')
    ts = calendar.timegm(mydate.utctimetuple())
    return ts;

def subtract_times(ts2,ts1):
    t2str = base_date + ' ' + ts2
    t1str = base_date + ' ' + ts1

    t2 = get_feedback_datestr_as_timestamp(t2str)
    t1 = get_feedback_datestr_as_timestamp(t1str)

    dt = t2 - t1

    dt /= 60
    return dt

def get_events(filename):
    count = 0
    events = []
    with open(filename) as csvfile:
        reader = csv.DictReader(csvfile,delimiter=',')
        
        for row in reader:
            dt = subtract_times(row['new_time'],row['old_time'])
            event = {'dt': dt,
                     'account_id' : row['account_id'],
                     'date_of_night' : row['date_of_night'],
                     'event_type' : row['event_type'],
                     'new_time' : row['new_time']}

            events.append(event)
            count += 1


    return events,count


                                

                                
