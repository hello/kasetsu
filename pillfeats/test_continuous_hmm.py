#!/usr/bin/python
import pillcsv
import sensecsv
import surveycsv
import all_data
import os.path
import json
from numpy import *
from pylab import *
import sklearn.mixture
import sys
from hmm.continuous.PoissonHMM import PoissonHMM
from time import strftime
import datetime
import csv
import argparse

import data_windows

save_filename = 'savedata3.json'

k_min_count_pill_data = 250
k_min_num_days_of_sense_data = 5
k_min_date = '2015-01-01'
k_min_m_val = 4.0

k_default_energy = 50

k_period_in_seconds = 15 * 60.0
k_segment_spacing_in_seconds = 120 * 60.0
k_min_segment_length_in_seconds = 240*60.0
k_segment_padding_in_seconds = 180 * 60.0

NUMITER = 10
 
def pull_data():
    import dbdata
    import os.path
 
    
    if os.path.isfile(save_filename): 
        print 'loading from %s' % save_filename
        f = open(save_filename, 'r')
        data = json.load(f)
        f.close()
    else:
        d = dbdata.DataGetter('benjo','benjo','localhost')
        print 'querying DB'
        data = d.get_all_minute_data(k_min_date,1440 * k_min_num_days_of_sense_data,k_min_count_pill_data)
        f = open(save_filename, 'w')
        json.dump(data, f)
        f.close()


    return data


def get_sleep_times(t, path):
    n = len(path)
    
    sleep_times = []
    wake_times = []
    
    for i in xrange(1, n):
        prev = path[i-1]
        current = path[i]
        tprev = t[i-1]
        tcurrent = t[i]
        
        if current == 3 and (prev == 0 or prev == 1 or prev == 2):
            sleep_times.append(tcurrent)
            
        if (current == 6 or current == 7) and (prev == 5):
            wake_times.append(tprev)
            
    return sleep_times, wake_times

def get_unix_time_as_datetime(unix_time):
    return datetime.datetime.fromtimestamp(unix_time)
        

if __name__ == '__main__':
    
    parser = argparse.ArgumentParser()
    #parser.add_argument("-t",  "--train",help="evaluate,train", required=True, type=str)
    parser.add_argument('-t', '--train', action='store_true', default=False)
    parser.add_argument("-f",  "--file", help="output file of predicted sleep / wake times")
    parser.add_argument("-m",  "--model", help="model file (usually a .json)")
    parser.add_argument("-u",  "--user",  help="particular user to train on / evaluate, otherwise we do all users in database")
    parser.add_argument("--iter", help="number of training iterations", default=8)
    args = parser.parse_args()
    set_printoptions(precision=3, suppress=True, threshold=np.nan)
    
    
    #states
    # 0 - off bed (dark, no activity)
    # 1 - reading on bed (light, high activity)
    # 2 - watching movie on bed (dark, high activity)
    # 3 - sleep (dark, low activity)
    # 4 - tossing / turning (dark, high activity)
    # 5 - waking up (light, low activity)
    # 6 - lazy sunday (light, high activity) 
    # 7 - woke up (light, no activity)
    
    A = array([
    [0.84, 0.05, 0.05, 0.05, 0.00, 0.00, 0.00, 0.01],
    [0.00, 0.80, 0.10, 0.10, 0.00, 0.00, 0.00, 0.00],
    [0.00, 0.10, 0.80, 0.10, 0.00, 0.00, 0.00, 0.00], 
    [0.00, 0.00, 0.00, 0.85, 0.10, 0.05, 0.00, 0.00], 
    [0.00, 0.00, 0.00, 0.50, 0.50, 0.00, 0.00, 0.00], 
    [0.00, 0.00, 0.00, 0.00, 0.00, 0.90, 0.05, 0.05], 
    [0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.90, 0.10], 
    [0.10, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.90]

    ])
             
             
    pi0 = array([0.65, 0.05, 0.05, 0.05, 0.05, 0.05, 0.05, 0.05])
        
    #light, then counts
    means = [[1.0, 6.0, 1.0, 1.0, 1.0, 6.0, 6.0, 6.0],
             [0.1, 6.0, 6.0, 1.0, 4.0, 1.0, 8.0, 0.1]]
    
    hmm = PoissonHMM(8,2, A,pi0, means, verbose=True )
    
    
    data = pull_data()
   
    all_times = []
    flat_seg = []
    packaged_info = []
    count = 0
    
    if args.user != None:
        if not data.has_key(args.user):
            print ('user does not exist in data set! quitting....')
            sys.exit(0)
        else:
            data = {args.user : data[args.user]}
    
    
    keys = data.keys()
    
    
    for key in data:
        
        t, l, c = data_windows.data_to_windows(data[key], k_period_in_seconds)
        l[where(l < 0)] = 0.0
        l = (log(l + 1.0)).astype(int)
        '''
        plot(t, c)
        plot(t, log(l + 10.0))
        show()
        '''
        
        for i in xrange(len(t)):
            flat_seg.append([l[i], c[i]])

        count += 1
        
        #if count > 4:
        #    break;
       
        
    flat_seg = array(flat_seg)
    print flat_seg.shape
    
    if args.model != None:
        f = open(args.model, 'r')
        hmm.from_dict(json.load(f))
    
    
    if args.train != None and args.train != False:
        print ('TRAINING')
        hmm.train(flat_seg, NUMITER)
        filename = strftime("HMM_%Y-%m-%d_%H:%M:%S.json")
        print ('saving to %s' % filename)

        f = open(filename, 'w')
        json.dump(hmm.to_dict(), f)
        f.close()
    
    print hmm.A
    print hmm.thetas
    
  
    
    outfile = args.file
   
        
    sleep_segments = []
    for key in keys:
        
        t, l, c = data_windows.data_to_windows(data[key], k_period_in_seconds)
        l[where(l < 0)] = 0.0
        l = (log(l + 1.0)).astype(int)
        '''
        plot(t, c)
        plot(t, log(l + 10.0))
        show()
        '''
        
        seg = []
        for i in xrange(len(t)):
            seg.append([l[i], c[i]])
        
        seg = array(seg)
        path = hmm.decode(seg)
        
        sleep_times, wake_times = get_sleep_times(t, path)        
        sleeps = array([get_unix_time_as_datetime(f).strftime('%Y-%m-%d %H:%M:%S') for f in sleep_times])
        wakes = array([get_unix_time_as_datetime(f).strftime('%Y-%m-%d %H:%M:%S') for f in wake_times])
        
       

        if outfile == None:
            figure(1)
            ax = subplot(2, 1, 1)
            plot(t, l)
            plot(t, c)
            
            title(key)
            grid('on')
            
            subplot(2, 1, 2, sharex=ax)
            plot(t, path, 'k.-')
            grid('on')
            show()
        
        if len(sleeps) != len(wakes):
            print 'error for user %d, number of sleeps does not equal number of wakes' % int(key)
            continue
        
        durations_in_hours =  (array(wake_times) - array(sleep_times)) / 3600.0
        bad_idx = where(durations_in_hours < 2)
        
        sleeps = delete(sleeps, bad_idx)
        wakes = delete(wakes, bad_idx)
        durations_in_hours = delete(durations_in_hours, bad_idx)
        
        print durations_in_hours
        

        for i in xrange(len(sleeps)):
            sleep_segments.append((key, sleeps[i], wakes[i]))
        
    
    if outfile != None:
        with open(outfile, 'wb') as csvfile:
            mywriter = csv.writer(csvfile, delimiter=',')
            
            for seg in sleep_segments:
                mywriter.writerow(seg)
                
        csvfile.close()
            
        
    
