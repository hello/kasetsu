#!/usr/bin/python

import csv
import sys
import datetime
from math import *
import copy
import pytz
import calendar

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

def sensor_data_vector_from_line(line):
    acc = line[0]
    t = read_time(line[1])

    x = []
    for i in range(2,len(line)):
        x.append(float(line[i]))

    x[0] = log(x[0]*256 / float(2 ** 16) + 1.0) / log(2)
    x[1] = 0;
    x[4] = x[4] / 1024.0 / 10. - 4.
    if x[4] < 0: x[4] = 0
    x[7] /= 10000.
    
    return acc,t,x

    
def read_input_file(filename):
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

    print '%d users' % len(all_sensor_data)

    return accs,times,all_sensor_data            

def read_label_file(filename):
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

def create_labels_for_day(accounts,times,data,labels):
    t1 = times[0][0];
    t2 = times[0][-1];

    for i,account in enumerate(accounts):
        if not labels.has_key(account):
            continue

        xx = labels[account]
        L = []
        for x in xx:
            if x >= t1 and x <= t2:
                L.append(x)
      
        if len(L) > 0:
            print L

        


if __name__ == '__main__':
    sleeps,wakes=read_label_file('labels_sleep_2016-01-01_2016-03-02.csv000')
    accounts,times,data=read_input_file('2016-01-04.csv000')
    create_labels_for_day(accounts,times,data,wakes)   
