#!/usr/bin/python

import csv
import sys
import datetime
from math import *
import copy

def sensor_data_vector_from_line(line):
    acc = line[0]
    dstr = line[1]
    t = datetime.datetime.strptime(dstr,'%Y-%m-%d %H:%M:%S')

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

if __name__ == '__main__':
    read_input_file('2016-01-04.csv000')

