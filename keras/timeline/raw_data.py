#!/usr/bin/python

import csv
import sys
import datetime
from math import *
import copy
import pytz
import calendar
import bisect
#from matplotlib.pyplot import *

k_num_labels = 2

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
            x[4] = x[4] / 1024.0 / 10. - 4.
            if x[4] < 0: x[4] = 0
            x[7] /= 10000.
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

        wakes = {}
        sleeps = {}
        
        for line in reader:
            acc = line[0]
            t = read_time(line[1])
            t1 = read_24_hr_time(t,line[2])
            t2 = read_24_hr_time(t,line[3])

            if not wakes.has_key(acc):
                wakes[acc] = []

            if not sleeps.has_key(acc):
                sleeps[acc] = []

            sleeps[acc].append(get_timestamp(t1))
            wakes[acc].append(get_timestamp(t2))

    return sleeps,wakes

#accounts is list of accounts, matched by index with times and data
#labels is a map by account, with a list of label times (which may exceed the
#current day)
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
            if x >= t1 and x <= t2:
                L.append(x)
      

        indexed_labels[i].extend(L)

    return indexed_labels
        

def insert_event_labels(labels,times,event_times,ipre,ipost,radius):
    indices = [bisect.bisect(times,t) for t in event_times]

    for idx in indices:
        for i in range(idx-radius,idx+radius):
            if i < 0 or i >= len(times):
                continue

            if i >= idx:
                labels[i][ipost] = 1.0

            if i < idx:
                labels[i][ipre] = 1.0
    
def load_data(list_of_data_files,label_file):
    sleeps,wakes=read_label_file(label_file)

    data = []
    for filename in list_of_data_files:
        accounts,times,rawdata=read_input_file(filename)
        process_raw_data(times,rawdata)
        indexed_labels = extract_label_times_for_day(accounts,times,wakes)
        indexed_labels2 = extract_label_times_for_day(accounts,times,sleeps)

        label_vecs = []
        for ts,L,L2 in zip(times,indexed_labels,indexed_labels2):
            if len(L) and len(L2) == 0:
                label_vecs.append([])
                continue

            
            labels = [[0 for i in range(k_num_labels)] for t in ts]
            insert_event_labels(labels,ts,L,1,0,30)
            insert_event_labels(labels,ts,L2,0,1,30)
            label_vecs.append(labels)


        data.extend(zip(rawdata,label_vecs))

    return data


if __name__ == '__main__':
    labels_file = 'labels_sleep_2016-01-01_2016-03-02.csv000'
    raw_data_files = ['2016-01-04.csv000']

    data = load_data(raw_data_files,labels_file)
    print data[30][1]
    print len(data)
#    plot(data[30][1])
#    show()
