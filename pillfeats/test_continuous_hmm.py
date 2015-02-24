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
from hmm.continuous.CompositeModelHMM import CompositeModelHMM
from time import strftime
import datetime
import csv
import argparse
import copy

import data_windows

save_filename = 'savedata3.json'

k_min_count_pill_data = 40
k_min_num_days_of_sense_data = 2.5
k_min_date = '2015-02-15'

k_period_in_seconds = 15 * 60.0
k_segment_spacing_in_seconds = 120 * 60.0
k_min_segment_length_in_seconds = 240*60.0
k_segment_padding_in_seconds = 180 * 60.0
k_min_sleep_duration_hours = 1.5
light_sleep_limit = 6 #periods

k_raw_light_to_lux = 125.0 / (2 ** 16)
k_lux_multipler = 4.0

not_on_bed_states = [0, 1]
on_bed_states = [2, 3, 4, 5, 6, 7, 8]
wake_states = [0, 1, 2, 3, 7, 8]
sleep_states = [4, 5, 6]
light_sleep_state = 6

forbidden_keys = [1057]

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
        d = dbdata.DataGetter('benjo_sensors_1','benjo','localhost')
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
        

def make_poisson(mean, obsnum):
    return {'model_type' : 'poisson' ,  'model_data' : {'obs_num' : obsnum, 'mean' : mean}}
    
def make_uniform(mean, obsnum):
    return {'model_type' : 'uniform' ,  'model_data' : {'obs_num' : obsnum, 'mean' : mean}}
    
def make_discrete(dist, obsnum):
    return {'model_type' : 'discrete_alphabet' ,  'model_data' : {'obs_num' : obsnum,  'alphabet_probs' : dist}}

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
    # 0 - off bed #1 (very low activity,low light)
    # 1 - off bed #2 (very low activity,high light)
    # 2 - reading on bed (high activity, high light)
    # 3 - ipad on bed    (high activity, low light)
    # 4 - sleep (low activity, low light)
    # 5 - disturbed sleep (high activity, low light)
    # 6 - late sleep (med light, low activity)
    # 7 - waking up with alarm (med light, med activity, high wave)
    # 8 - woken up (med light, high activity) 
    
    A = array([
    [0.70, 0.10, 0.10, 0.10, 0.00, 0.00, 0.00, 0.00, 0.00], 
    [0.10, 0.70, 0.10, 0.10, 0.00, 0.00, 0.00, 0.00, 0.00], 
    [0.00, 0.05, 0.70, 0.10, 0.15, 0.00, 0.00, 0.00, 0.00], 
    [0.00, 0.00, 0.10, 0.70, 0.20, 0.00, 0.00, 0.00, 0.00], 
    [0.00, 0.00, 0.00, 0.00, 0.60, 0.25, 0.05, 0.05, 0.05], 
    [0.00, 0.00, 0.00, 0.00, 0.40, 0.50, 0.00, 0.00, 0.00], 
    [0.05, 0.05, 0.00, 0.00, 0.00, 0.00, 0.70, 0.10, 0.10], 
    [0.10, 0.10, 0.00, 0.00, 0.00, 0.00, 0.00, 0.70, 0.10], 
    [0.10, 0.10, 0.00, 0.00, 0.00, 0.00, 0.00, 0.10, 0.70]
    ])
             
             
    pi0 = array([0.60, 0.05, 0.05, 0.05, 0.05, 0.05, 0.05, 0.05, 0.05])
        
    #light, then counts, then waves, then sound, then energy
       
    low_light = 0.5
    med_light = 3.0
    high_light = 6.0
    
    no_motion = 0.05
    low_motion = 3.0
    med_motion = 4.0
    high_motion = 8.0
    
    no_waves = [0.999, 0.001]
    low_waves = [0.9, 0.1]
    med_waves = [0.5, 0.5]
    high_waves = [0.1, 0.9]
    
    #                 light,                        counts,                     waves,                       sound,                energy
    model0 = [make_poisson(low_light, 0),  make_poisson(no_motion, 1),   make_discrete(low_waves, 2)]
    model1 = [make_poisson(high_light, 0), make_poisson(no_motion, 1),   make_discrete(low_waves, 2)] 
    model2 = [make_poisson(high_light, 0), make_poisson(high_motion, 1), make_discrete(low_waves, 2) ]
    model3 = [make_poisson(low_light, 0),  make_poisson(high_motion, 1), make_discrete(low_waves, 2)]
    model4 = [make_poisson(low_light, 0),  make_poisson(low_motion, 1),  make_discrete(no_waves, 2)]
    model5 = [make_poisson(low_light, 0),  make_poisson(high_motion, 1), make_discrete(no_waves, 2)]
    model6 = [make_poisson(med_light, 0),  make_poisson(low_motion, 1),  make_discrete(no_waves, 2)]
    model7 = [make_poisson(med_light, 0),  make_poisson(med_motion, 1),  make_discrete(high_waves, 2)]
    model8 = [make_poisson(high_light, 0), make_poisson(high_motion, 1), make_discrete(low_waves, 2)]


    models = [model0, model1, model2, model3, model4, model5, model6, model7, model8]

    hmm = CompositeModelHMM(models, A, pi0, verbose=True)
    
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
            
        t, l, c, sc, energy, waves = data_windows.data_to_windows(data[key], k_period_in_seconds)
        sc[where(sc < 0)] = 0.0
        waves[where(waves > 0)] = 1.0;
        sc = log2(sc + 1.0).astype(int)
        l[where(l < 0)] = 0.0
        l = (log2(k_raw_light_to_lux*l * k_lux_multipler + 1.0)).astype(int)
        energy[where(energy < 0)] = 0.0
        energy = log2((energy + 500)/500).astype(int)

        
        '''
        plot(t, c)
        plot(t, log(l + 10.0))
        show()
        '''
        
        for i in xrange(len(t)):
            flat_seg.append([l[i], c[i], waves[i],  sc[i], energy[i]])

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
    print hmm.get_status()
  
    
    outfile = args.file
    
    if outfile != None and os.path.isfile(outfile):
        os.remove(outfile)

        
    sleep_segments = []
    for key in keys:
        
        if key in forbidden_keys:
            continue
        
        t, l, c, sc, energy, waves = data_windows.data_to_windows(data[key], k_period_in_seconds)
        sc[where(sc < 0)] = 0.0
        waves[where(waves > 0)] = 1.0;

        sc = log2(sc + 1.0).astype(int)

        l[where(l < 0)] = 0.0
        l = (log2(l*k_raw_light_to_lux*k_lux_multipler + 1.0)).astype(int)
        energy[where(energy < 0)] = 0.0
        energy = log2((energy + 500)/500).astype(int)
        
        '''
        plot(t, c)
        plot(t, log(l + 10.0))
        show()
        '''
        
        seg = []
        for i in xrange(len(t)):
            seg.append([l[i], c[i],waves[i], sc[i], energy[i]])
        
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
        #model_cost = myhmm.forwardbackward(seg)
        #model_cost /= len(seg) / myhmm.d
        #print 'AVERAGE MODEL COST = %f' % model_cost
        #path_cost = myhmm.evaluate_path_cost(seg, path, len(seg))
        #limit = 3.0 * mean(path_cost)
        #score = sum(path_cost > limit)
        
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
            plot(t2, sc)
            plot(t2, energy)
            plot(t2, waves)
            legend(['log light', 'pill wake counts', 'log sound counts', 'log energy', 'wavecount'])
            
            #title("userid=%s, %d periods > %f, model cost=%f" % (str(key), score, limit, model_cost))
            title("userid=%s" % (str(key)))
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
                
        
    
