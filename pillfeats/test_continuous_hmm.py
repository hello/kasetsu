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
import copy

import data_windows

save_filename = 'savedata3.json'

k_min_count_pill_data = 250
k_min_num_days_of_sense_data = 5
k_min_date = '2015-01-20'

k_default_energy = 50

k_period_in_seconds = 15 * 60.0
k_segment_spacing_in_seconds = 120 * 60.0
k_min_segment_length_in_seconds = 240*60.0
k_segment_padding_in_seconds = 180 * 60.0
k_min_sleep_duration_hours = 1.5
light_sleep_limit = 6 #periods

not_on_bed_states = [0, 7]
on_bed_states = [1, 2, 3, 4, 5, 6]
wake_states = [0, 1, 2, 6, 7]
sleep_states = [3, 4, 5]

forbidden_keys = [1781]

def get_unix_time_as_datetime(unix_time):
    return datetime.datetime.utcfromtimestamp(unix_time)
    
def get_unix_time_as_string(unix_time): 
    return get_unix_time_as_datetime(unix_time).isoformat(' ')   

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

mode_on_bed = 'a'
mode_off_bed = 'b'
mode_sleeping = 'c'
mode_not_sleeping = 'd'

def get_sleep_times(t, path):
    events = []
    light_sleep_state = 5
    light_sleep_count = 0
    
    sleep_times = [0, 0]
    bed_times = [0, 0]
    
    bed_mode = mode_off_bed
    sleep_mode = mode_not_sleeping
    
    for idx in xrange(len(path)):
        state = path[idx]
        
            
        #track how long in the light sleep state
        if state == light_sleep_state:
            light_sleep_count += 1
            
        if state in wake_states:
            new_sleep_mode = mode_not_sleeping
            
        if state in sleep_states:
            new_sleep_mode = mode_sleeping;

            
        #####################
        #off bed? zero out light sleep counter
        if state in not_on_bed_states:
            light_sleep_count = 0
            new_bed_mode = mode_off_bed

        if state in on_bed_states:
            new_bed_mode = mode_on_bed
        
        #################################
        #too many light sleep modes? get up.
        if light_sleep_count >= light_sleep_limit:
            new_sleep_mode = mode_not_sleeping;   
            
        #did you just start sleeping?
        if new_sleep_mode == mode_sleeping and sleep_mode == mode_not_sleeping:
            sleep_times[0] = t[idx]
            
        #did you just stop sleeping?
        if new_sleep_mode == mode_not_sleeping and sleep_mode == mode_sleeping:
            sleep_times[1] = t[idx]
            
        #did you just get on the bed?
        if new_bed_mode == mode_on_bed and bed_mode == mode_off_bed:
            bed_times[0] = t[idx]
            
            
        #did you just get off the bed?
        if new_bed_mode == mode_off_bed and bed_mode == mode_on_bed:
            bed_times[1] = t[idx]
            
            event = [bed_times[0] ,  sleep_times[0] ,  sleep_times[1] , bed_times[1]]

            if bed_times[0] <= sleep_times[0] < sleep_times[1] <= bed_times[1]:
                events.append(copy.deepcopy(event))
            else:
                print 'bad event!', event
                
        bed_mode = new_bed_mode
        sleep_mode = new_sleep_mode
            
        
    return events
        

if __name__ == '__main__':
    
    parser = argparse.ArgumentParser()
    #parser.add_argument("-t",  "--train",help="evaluate,train", required=True, type=str)
    parser.add_argument("-f",  "--file", help="output file of predicted sleep / wake times")
    parser.add_argument("-m",  "--model", help="model file (usually a .json)")
    parser.add_argument("-u",  "--user",  help="particular user to train on / evaluate, otherwise we do all users in database")
    parser.add_argument("--iter", type=int, help="number of training iterations", default=8)
    parser.add_argument("--adapt", action='store_true', default=False, help='compute a model for each individual user ids')
    parser.add_argument('--train', action='store_true', default=False, help='compute an aggregate model for all user ids')
    parser.add_argument('--saveadapt', action='store_true', default=False, help='save the adaptation for each user')

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
    [0.75, 0.05, 0.05, 0.05, 0.00, 0.00, 0.00, 0.10],
    [0.00, 0.80, 0.10, 0.10, 0.00, 0.00, 0.00, 0.00],
    [0.00, 0.10, 0.80, 0.10, 0.00, 0.00, 0.00, 0.00], 
    [0.00, 0.00, 0.00, 0.80, 0.10, 0.05, 0.05, 0.00], 
    [0.00, 0.00, 0.00, 0.50, 0.50, 0.00, 0.00, 0.00], 
    [0.05, 0.00, 0.00, 0.00, 0.00, 0.85, 0.05, 0.05], 
    [0.10, 0.00, 0.00, 0.00, 0.00, 0.00, 0.80, 0.10], 
    [0.10, 0.05, 0.05, 0.05, 0.00, 0.00, 0.00, 0.75]

    ])
             
             
    pi0 = array([0.65, 0.05, 0.05, 0.05, 0.05, 0.05, 0.05, 0.05])
        
    #light, then counts
    means = [[1.0, 6.0, 1.0, 1.0, 1.0, 6.0, 6.0, 6.0],
             [0.01, 6.0, 6.0, 1.0, 4.0, 1.0, 8.0, 0.01]]
    
    hmm = PoissonHMM(8,2, A,pi0, means, verbose=True )
    
    
    data = pull_data()
   
    all_times = []
    flat_seg = []
    packaged_info = []
    count = 0
    hmm_dict = {}
    dict_filename = strftime("HMM_%Y-%m-%d_%H:%M:%S.json")

    
    if args.user != None:
        print args.user
        if not data.has_key(args.user):
            print ('user does not exist in data set! quitting....')
            sys.exit(0)
        else:
            data = {args.user : data[args.user]}
    
    keys = data.keys()
    print keys

    
    for key in data:
        
        if key in forbidden_keys:
            continue 
            
        t, l, c, sc, energy = data_windows.data_to_windows(data[key], k_period_in_seconds)
        l[where(l < 0)] = 0.0
        l = (log(l + 1.0)).astype(int)
        energy[where(energy < 0)] = 0.0
        energy = log(energy + 1.0).astype(int)
        
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
        hmm_dict = json.load(f)
        hmm.from_dict(hmm_dict['default'])

    
    
    if args.train == True:
        print ('TRAINING')
        hmm.train(flat_seg, args.iter)
        
        print ('saving to %s' % dict_filename)

        hmm_dict['default'] = hmm.to_dict()

        f = open(dict_filename, 'w')
        json.dump(hmm_dict, f)
        f.close()
        
    
    print hmm.A
    print hmm.thetas
    
  
    
    outfile = args.file
    
    if outfile != None and os.path.isfile(outfile):
        os.remove(outfile)

        
    sleep_segments = []
    for key in keys:
        
        if key in forbidden_keys:
            continue
        
        t, l, c, sc, energy = data_windows.data_to_windows(data[key], k_period_in_seconds)
        l[where(l < 0)] = 0.0
        l = (log(l + 1.0)).astype(int)
        energy[where(energy < 0)] = 0.0
        energy = log(energy + 1.0).astype(int)
        '''
        plot(t, c)
        plot(t, log(l + 10.0))
        show()
        '''
        
        seg = []
        for i in xrange(len(t)):
            seg.append([l[i], c[i]])
        
        seg = array(seg)
        
        myhmm = copy.deepcopy(hmm)
        
        if hmm_dict.has_key(key):
            print 'USING CUSTOM MODEL for key=%s' % (str(key))
            myhmm.from_dict(hmm_dict[key])
        else:
            print 'USING DEFAULT MODEL for key=%s' % (str(key))

        if args.adapt:
            print ('ADAPTING for %s' % str(key))
            myhmm.train(seg, args.iter)
            
            if args.saveadapt:
                hmm_dict[key] = myhmm.to_dict()
                f = open(dict_filename, 'w')
                json.dump(hmm_dict, f)
                f.close()
            
        
        path = myhmm.decode(seg)
        model_cost = myhmm.forwardbackward(seg)
        model_cost /= len(seg) / myhmm.d
        print 'AVERAGE MODEL COST = %f' % model_cost
        path_cost = myhmm.evaluate_path_cost(seg, path, len(seg))
        limit = 3.0 * mean(path_cost)
        score = sum(path_cost > limit)
        
        events = get_sleep_times(t, path)   

        sleep_time_strings = []
        good_events = []
        for e in events:
            if len(e) >= 4:
                sleep_duration = (e[2] - e[1]) / 3600.0
                
                if sleep_duration > k_min_sleep_duration_hours:
                
                    sleep_time_strings.append(  [get_unix_time_as_string(e[0]), 
                                         get_unix_time_as_string(e[1]), 
                                         get_unix_time_as_string(e[2]), 
                                         get_unix_time_as_string(e[3]), 
                                         sleep_duration] )
                                         
                    good_events.append(e)
                    
        
        events = good_events
        
        for s in sleep_time_strings:
            print s

        if outfile == None:
            t2 = [get_unix_time_as_datetime(tt) for tt in t]
            figure(1)
            ax = subplot(2, 1, 1)
            plot(t2, l)
            plot(t2, c)
            plot(t2, log2(sc + 1.0))
            plot(t2, energy)
            legend(['log light', 'pill wake counts', 'log sound counts', 'log energy'])
            
            title("userid=%s, %d periods > %f, model cost=%f" % (str(key), score, limit, model_cost))
            grid('on')
            
            subplot(2, 1, 2, sharex=ax)
            plot(t2, path, 'k.-')
            #plot(t2, path_cost, 'ro')
            grid('on')
            
            show()
    
        else:
            with open(outfile, 'a') as csvfile:
                mywriter = csv.writer(csvfile, delimiter=',')
                
                for item in events:
                    row = [key]
                    row.extend(item)
                    
                    mywriter.writerow(row)
                    
            csvfile.close()
                
        
    
