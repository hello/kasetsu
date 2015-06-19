#!/usr/bin/python

import serverdata
import numpy as np
import datetime
import matplotlib.dates as mdates
import scipy.signal
import argparse
from matplotlib.pyplot import *

k_num_minutes_smoothed = 5
light_offset = 0.0
    
def fill_zeros_if_none(data):
    for i in xrange(len(data)):
        vec =data[i]
        
        for i in xrange(len(vec)):
            if vec[i] == None:
                vec[i] = 0
                
def smooth(x):
    a = np.array([1])
    b = np.ones((k_num_minutes_smoothed, )) / float(k_num_minutes_smoothed)
    x2 = scipy.signal.filtfilt(b, a, x)
    
    return x2
    
def plot_data(mydict):
    keys = mydict.keys()
    print keys
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


        print 'got %d sense points' % (len(times))            
        times = np.array(times)
        kickoff_counts = np.array(data[9])
        svm_mag = np.array(data[5] ) / 2000.0
        pillrange = np.array(data[7])  / 4096.0
        duration = np.array(data[8])
        soundmag = np.array(data[4]) / 10.0
        wave = np.array(data[6])
        light = np.array(data[2])
        light = light - light_offset
        light[np.where(light < 0.0)] = 0.0
        light = np.log2(4.0 * light + 1.0)
        ax = subplot(1,1,1)
        ax.fmt_xdata = mdates.DateFormatter('%Y-%m-%d | %H:%M')
        plot(
        times,smooth(light),
        times,smooth(kickoff_counts), '.-', 
        times, svm_mag, 'o', 
        times, pillrange, 'o', 
        times, smooth(duration), '.-', 
        times, soundmag, '+',
        times, wave,'h'); 
        grid('on')
        legend(['light','counts', 'mag', 'range', 'duration', 'soundmag','waves'])
        title('userid=%s' % str(key))
        show()

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--date', help = 'target date')
    parser.add_argument('-n','--numdays',default=1, help = 'num days to retrieve')
    parser.add_argument('-u','--user',help='user id number')
    args = parser.parse_args()

    users = [int(args.user)]
 
    getter = serverdata.ServerDataGetter(users)

    num_days = int(args.numdays)
   
    date = args.date
    print date,users,num_days 
    data = getter.get_all_minute_data(args.date, num_days) 
    plot_data(data)
