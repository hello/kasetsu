#!/usr/bin/python

import csv
import sys
import datetime
from math import *
import copy
import pytz
import calendar
import bisect
import numpy as np
from collections import defaultdict
from multiprocessing import Pool


k_num_labels = 3
k_radius = 120
k_uncertainty = 10

k_label_map = {'14' : (1,2), '12' : (0,1)}

def get_timestamp(dt):
    return calendar.timegm(dt.utctimetuple())

def read_24_hr_time(orig_time,dstr):
    t =  datetime.datetime.strptime(dstr,'%H:%M')
    t2=datetime.datetime(year=orig_time.year,month=orig_time.month,day=orig_time.day,hour=t.hour,minute=t.minute)
    
    if t.hour <= 14:
        t2 += datetime.timedelta(days=1)

    return t2


def read_time(dstr):
    return datetime.datetime.strptime(dstr,'%Y-%m-%d %H:%M:%S')

def process_raw_data(times,rawdata):
    for idx in range(len(times)):
        xx = rawdata[idx]
        tt = times[idx]

        lastx = None
        for i,x in enumerate(xx):
            t = tt[i]
            x[0] = log(x[0]*256 / float(2 ** 16) + 1.0) / log(2)
            x[1] = 0;
            x[3] /= 2.0;
            x[4] = x[4] / 1024.0 / 10. - 4.
            if x[4] < 0: x[4] = 0
            x[5] /= 5.0
            x[6] /= 5.0
            x[7] /= 5000.
            dt = datetime.datetime.fromtimestamp(t,pytz.UTC)

            if i > 1:
                x[1] = x[0] - lastx[0]

            lastx = copy.deepcopy(x)
            #if between 5am and 6pm, zero out light
            if dt.hour >= 5 and dt.hour <= 18:
                x[0] = 0


                
def sensor_data_vector_from_line(line):
    acc = line[0]
    t = read_time(line[1])

    x = []
    for i in range(2,len(line)):
        x.append(float(line[i]))

 
    
    return acc,t,x

    
def read_input_file(filename):
    print "opening %s..." % filename
    with open(filename,'rb') as f:
        reader = csv.reader(f)
        prev_account_id = None
        all_sensor_data = []
        accs = []
        times = []
        
        for line in reader:
            acc,dt,x = sensor_data_vector_from_line(line)
            t = get_timestamp(dt)

            if prev_account_id != acc:
                if prev_account_id != None:
                    all_sensor_data.append(copy.deepcopy(xx))
                    accs.append(prev_account_id)
                    times.append(tt)
                    
                xx = []
                tt = []

            xx.append(x)
            tt.append(t)
            
            prev_account_id = acc

    #print '%d users' % len(all_sensor_data)

    return accs,times,all_sensor_data            

def read_label_file(filename):
    print "opening %s..." % filename
    with open(filename,'rb') as f:
        reader = csv.reader(f)

        events = {}
        
        for line in reader:
            acc = line[0]
            date_of_night = read_time(line[1])
            t1 = read_24_hr_time(date_of_night,line[2])
            event_type = line[3]

            if not events.has_key(acc):
                events[acc] = []


            events[acc].append((get_timestamp(t1),event_type))

    return events

#accounts is list of accounts, matched by index with times and data
#labels is a map by account, with a list of label times (which may exceed the
#current day)
#labels is a map by account_id where the value is a list of label tuples (time,label_type)
#the goal here is to just find the times for the timespan and account_id of interest
def extract_label_times_for_day(accounts,times,labels):
    t1 = times[0][0];
    t2 = times[0][-1];

    indexed_labels = []
    for i,account in enumerate(accounts):
        indexed_labels.append([])
        if not labels.has_key(account):
            continue

        xx = labels[account]
        L = []
        for x in xx:
            #is in time bounds?
            if x[0] >= t1 and x[0] <= t2:
                L.append(x)
      

        indexed_labels[i].extend(L)

    return indexed_labels
        

def insert_event_labels(labels,times,L,radius,uncertainty):

    for t,event_type in L:
        idx = bisect.bisect(times,t)
        ipre,ipost = k_label_map[event_type]

        for i in range(idx-radius,idx+radius):
            if i < 0 or i >= len(times):
                continue

            if i >= idx + uncertainty:
                labels[i][ipost] = 1.0

            if i < idx - uncertainty:
                labels[i][ipre] = 1.0


def load_data_helper(my_input):
    filename,events = my_input
    accounts,times,rawdata=read_input_file(filename)

    process_raw_data(times,rawdata)

    indexed_labels = extract_label_times_for_day(accounts,times,events)

    label_vecs = []
    for ts,L in zip(times,indexed_labels):
        if len(L) == 0:
            label_vecs.append([])
            continue

        #default labels, set to "0" for all times and all labels 
        labels = [[0 for i in range(k_num_labels)] for t in ts]
        insert_event_labels(labels,ts,L,k_radius,k_uncertainty)
        label_vecs.append(labels)


    return zip(rawdata,label_vecs)
        
def load_data(list_of_data_files,label_files):
    events = defaultdict(list)

    for label_file in label_files:
        new_events = read_label_file(label_file)

        for key in new_events:
            events[key].extend(new_events[key])

    my_pool = Pool(8)

    inputs = []
    for filename in list_of_data_files:
        inputs.append((filename,events))
    
    results = my_pool.map(load_data_helper,inputs)
    
    data = []
    for result in results:
        data.extend(result)
    
    return data

def get_inputs_from_data(data):
    print 'getting data...'

    dt = []
    for d in data:
        dt.append(len(d[0]))

    timesteps = np.median(dt)
    data_dim = len(d[0][0])
    nb_classes = len(d[1][0])

    data2 = []
    for d in data:
        if len(d[0]) == timesteps:
            data2.append(d)

    data = data2
    data2 = []
    for d in data:
        if len(d[1]) > 0:
            data2.append(d)

    print "found %d user-days" % len(data2)
    print "T=%d,N=%d,L=%d" % (timesteps,data_dim,nb_classes)

    #concatenate all the classes
    xx = []
    ll = []
    for x,l in data2:
        xx.append(x)
        ll.append(l)

    xx = np.array(xx)
    ll = np.array(ll)
    return xx,ll

if __name__ == '__main__':
    from matplotlib.pyplot import *
    labels_files = ['labels_et12_2016-01-01_2016-03-10.csv000', 'labels_et14_2016-01-01_2016-03-10.csv000'] 
    raw_data_files = ['any_sleep_or_wake_2016-01-01.csv000']

    data = load_data(raw_data_files,labels_files)
    count = 0
    for d in data: 
        plot(d[1]); show()
        count += 1
        if count > 10:
            break
