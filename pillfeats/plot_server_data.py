#!/usr/bin/python

import serverdata
import numpy as np
import datetime
from pylab import *

def fill_zeros_if_none(data):
    for i in xrange(len(data)):
        vec =data[i]
        
        for i in xrange(len(vec)):
            if vec[i] == None:
                vec[i] = 0

def plot_data(mydict):
    keys = mydict.keys()
    for key in keys:
        data = mydict[key]
            
        fill_zeros_if_none(data)
            
        t = data[0]
        offset = data[1]
        local_time_utc = np.array(t) + np.array(offset)
        
        local_time = local_time_utc.tolist()
        times = []
        for lt in local_time:
            times.append(datetime.datetime.utcfromtimestamp(lt))
            
        times = np.array(times)
        kickoff_counts = np.array(data[9])
        svm_mag = np.array(data[5] ) / 2000.0
        pillrange = np.array(data[7])  / 4096.0
        duration = np.array(data[8])
        plot(times, kickoff_counts, '.-', times, svm_mag, 'o', times, pillrange, 'o', times, duration, 'o'); 
        grid('on')
        legend(['counts', 'mag', 'range', 'duration'])
        show()

if __name__ == '__main__':
    users = [1062]
    getter = serverdata.ServerDataGetter(users)
    
    from_date_str = '2015-04-01'
    num_days = 1
    min_num_records = 20
    min_num_pill_records = 20
    
    data = getter.get_all_minute_data(from_date_str, num_days,  min_num_records, min_num_pill_records)
    plot_data(data)
