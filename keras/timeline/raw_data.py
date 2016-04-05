#!/usr/bin/python

import csv
import sys
import datetime
from math import *
import copy

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
            acc,t,x = sensor_data_vector_from_line(line)

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

    return accs,tt,all_sensor_data            

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

            sleeps[acc].append(t1)
            wakes[acc].append(t2)

    print sleeps
    return sleeps,wakes


if __name__ == '__main__':
    read_label_file('labels_sleep_2016-01-01_2016-03-02.csv000')
    read_input_file('2016-01-04.csv000')

