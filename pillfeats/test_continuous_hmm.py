#!/usr/bin/python
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
import sleep_hmm_pb2
import serverdata
import os.path

    
k_user_list = [1050, 1052, 1053, 1070, 1071, 1012, 1013, 1043, 1025, 1061, 1060, 1049, 1062, 1067, 1005, 1063, 1001, 1]

save_filename = 'savedata3.json'

k_min_count_pill_data = 0
k_min_num_days_of_sense_data = 0
k_min_date = '2015-02-22'
k_num_days_of_data = 14

k_period_in_seconds = 15 * 60.0
k_segment_spacing_in_seconds = 120 * 60.0
k_min_segment_length_in_seconds = 240*60.0
k_segment_padding_in_seconds = 180 * 60.0
k_min_sleep_duration_hours = 1.5
light_sleep_limit = 6 #periods

#k_raw_light_to_lux = 125.0 / (2 ** 16)
k_raw_light_to_lux = 1.0
k_lux_multipler = 4.0
k_sound_disturbance_threshold = 55.0
k_energy_disturbance_threshold = 15000
k_loglight_change_threshold = 2.0

on_bed_states = [4, 5, 6, 7, 8, 9, 10]
sleep_states = [6, 7, 8, 9]

light_sleep_state = [6]
regular_sleep_state = [7, 9]
disturbed_sleep_state = [8]

forbidden_keys = []


def to_proto(composite_hmm, user, timestring):
    print timestring
    filename = timestring + '.proto'
    
    sleep_hmm = sleep_hmm_pb2.SleepHmm()
    sleep_hmm.source = timestring
    sleep_hmm.user_id = user
    
    Nstates = len(composite_hmm.models)
    
    sleep_hmm.num_states = Nstates
    amat = array(composite_hmm.A).flatten().tolist()
    
    for entry in amat:
        sleep_hmm.state_transition_matrix.append(entry)
        
    pimat = array(composite_hmm.pi).flatten().tolist()
    
    for entry in pimat:
        sleep_hmm.initial_state_probabilities.append(entry)
    
    for i in xrange(Nstates):
        
        m_state = sleep_hmm.states.add()

        
        model =  composite_hmm.models[i]
        d = model.to_dict()
                
        m_light = sleep_hmm_pb2.GammaModel()
        m_light.mean = d[0]['model_data']['mean']
        m_light.stddev = d[0]['model_data']['stddev']
        
        m_motion_count = sleep_hmm_pb2.PoissonModel()
        m_motion_count.mean = d[1]['model_data']['mean']

        m_disturbances = sleep_hmm_pb2.DiscreteAlphabetModel()
        vec = d[2]['model_data']['alphabet_probs']
        for v in vec:
            m_disturbances.probabilities.append(v)
            
        m_soundcounts = sleep_hmm_pb2.GammaModel()
        m_soundcounts.mean = d[3]['model_data']['mean']
        m_soundcounts.stddev = d[3]['model_data']['stddev']

        m_state.light.MergeFrom(m_light)
        m_state.motion_count.MergeFrom(m_motion_count)
        m_state.disturbances.MergeFrom(m_disturbances)
        m_state.log_sound_count.MergeFrom(m_soundcounts)
        
        
        if i in sleep_states:
            m_state.sleep_mode = sleep_hmm_pb2.SLEEP
        else:
            m_state.sleep_mode = sleep_hmm_pb2.WAKE

        if i in on_bed_states:
            m_state.bed_mode = sleep_hmm_pb2.ON_BED
        else:
            m_state.bed_mode = sleep_hmm_pb2.OFF_BED
            
        if i in light_sleep_state:
            m_state.sleep_depth = sleep_hmm_pb2.LIGHT
        elif i in regular_sleep_state:
            m_state.sleep_depth = sleep_hmm_pb2.REGULAR
        elif i in disturbed_sleep_state:
            m_state.sleep_depth = sleep_hmm_pb2.DISTURBED
        else:
            m_state.sleep_depth = sleep_hmm_pb2.NOT_APPLICABLE

    
    f = open(filename, 'wb')
    f.write(sleep_hmm.SerializeToString())
    f.close()

        
    
    

def get_unix_time_as_datetime(unix_time):
    return datetime.datetime.utcfromtimestamp(unix_time)
    
def get_unix_time_as_string(unix_time): 
    return get_unix_time_as_datetime(unix_time).isoformat(' ')   

def pull_data():    
    if os.path.isfile(save_filename): 
        print 'loading from %s' % save_filename
        f = open(save_filename, 'r')
        data = json.load(f)
        f.close()
    else:
        print 'querying DB'

        #d = dbdata.DataGetter('benjo_sensors_1','benjo','localhost')
        #data = d.get_all_minute_data(k_min_date,1440 * k_min_num_days_of_sense_data,k_min_count_pill_data)

        d = serverdata.ServerDataGetter(k_user_list)
        data = d.get_all_minute_data(k_min_date, k_num_days_of_data, 1440 * k_min_num_days_of_sense_data,k_min_count_pill_data)
        
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
            
        if state not in sleep_states:
            new_sleep_mode = mode_not_sleeping
            
        if state in sleep_states:
            new_sleep_mode = mode_sleeping;

            
        #####################
        #off bed? zero out light sleep counter
        if state not in on_bed_states:
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
    
def make_discrete(dists, obsnum):
    return {'model_type' : 'discrete_alphabet' ,  'model_data' : {'obs_num' : obsnum,  'alphabet_probs' : dists}}
    
def make_gamma(mean, stddev, obsnum):   
    return {'model_type' : 'gamma' ,  'model_data' : {'obs_num' : obsnum, 'mean' : mean,  'stddev' : stddev}}

if __name__ == '__main__':
    
    parser = argparse.ArgumentParser()
    #parser.add_argument("-t",  "--train",help="evaluate,train", required=True, type=str)
    parser.add_argument("-f",  "--file", help="output file of predicted sleep / wake times")
    parser.add_argument("-m",  "--model", help="model file (usually a .json)")
    parser.add_argument("-u",  "--user",  help="particular user to train on / evaluate, otherwise we do all users in database")
    parser.add_argument("--iter", type=int, help="number of training iterations", default=4)
    parser.add_argument("--adapt", action='store_true', default=False, help='compute a model for each individual user ids')
    parser.add_argument('--train', action='store_true', default=False, help='compute an aggregate model for all user ids')
    parser.add_argument('--saveadapt', action='store_true', default=False, help='save the adaptation for each user')

    args = parser.parse_args()
    set_printoptions(precision=3, suppress=True, threshold=np.nan)
    
    
    low_light = 0.1
    med_light = 3.0
    high_light = 6.0
    low_light_stddev = 1.0
    ligh_stddev = 2.5
    
    no_motion = 0.01
    low_motion = 3.0
    med_motion = 4.0
    high_motion = 8.0
    

    low_wave = [0.9, 0.1]
    high_wave = [0.1, 0.9]
   
    sc_low = 1.0
    sc_high = 2.0
    sc_low_stddev = 0.5
    sc_high_stddev = 1.0
    
    #states
    # 0 - off bed #1 (very low activity,low light)
    # 1 - off bed #2 (very low activity,high light)
    # 2 - reading on bed (high activity, high light)
    # 3 - ipad on bed    (high activity, low light)
    # 4 - sleep (low activity, low light)
    # 5 - disturbed sleep (high activity, low light)
    # 7 - waking up with alarm (med light, med activity, high wave)
    # 8 - woken up (med light, high activity) 
    
    A = array([
    
    [0.65, 0.10, 0.10, 0.10,   0.10,  0.10,   0.00, 0.00, 0.00, 0.00,   0.00, 0.00], 
    [0.10, 0.65, 0.10, 0.10,   0.10,  0.10,   0.00, 0.00, 0.00, 0.00,   0.00, 0.00], 
    [0.10, 0.10, 0.65, 0.10,   0.10,  0.10,   0.00, 0.00, 0.00, 0.00,   0.00, 0.00], 
    [0.10, 0.10, 0.10, 0.65,   0.10,  0.10,   0.00, 0.00, 0.00, 0.00,   0.00, 0.00], 
    
    [0.05, 0.05, 0.05, 0.05,   0.70, 0.10,    0.10, 0.00, 0.00, 0.00,   0.00, 0.00], 
    [0.05, 0.05, 0.05, 0.05,   0.10, 0.65,    0.10, 0.05, 0.00, 0.00,   0.00, 0.00], 
    
    [0.00, 0.00, 0.00, 0.00,   0.00,  0.05,   0.55, 0.05, 0.10, 0.05,   0.10, 0.10], 
    [0.00, 0.00, 0.00, 0.00,   0.00,  0.05,   0.45, 0.50, 0.00, 0.00,   0.00, 0.00], 
    [0.00, 0.00, 0.00, 0.00,   0.00,  0.05,   0.45, 0.00, 0.50, 0.00,   0.00, 0.00], 
    [0.10, 0.00, 0.10, 0.00,   0.05,  0.00,   0.00, 0.00, 0.00, 0.65,   0.10, 0.10], 
    
    [0.10, 0.10, 0.10, 0.10,   0.00, 0.00,    0.00, 0.00, 0.00, 0.00,   0.60, 0.10], 
    [0.10, 0.10, 0.10, 0.10,   0.00, 0.00,    0.00, 0.00, 0.05, 0.00,   0.10, 0.55]
    ])
             
             
    pi0 = ones((A.shape[0], )) / A.shape[0]
        
    #light, then counts, then waves, then sound, then energy
       

    model0 = [make_gamma(high_light,ligh_stddev, 0),       make_poisson(no_motion, 1),     make_discrete(low_wave, 2),    make_gamma(sc_high, sc_high_stddev, 3)]
    model1 = [make_gamma(low_light,low_light_stddev, 0),   make_poisson(no_motion, 1),     make_discrete(low_wave, 2),    make_gamma(sc_high, sc_high_stddev, 3)]
    model2 = [make_gamma(high_light,ligh_stddev, 0),       make_poisson(no_motion, 1),     make_discrete(low_wave, 2),    make_gamma(sc_low, sc_low_stddev, 3)]
    model3 = [make_gamma(low_light,low_light_stddev, 0),   make_poisson(no_motion, 1),     make_discrete(low_wave, 2),    make_gamma(sc_low, sc_low_stddev, 3)]
    
    model4 = [make_gamma(high_light,ligh_stddev, 0),       make_poisson(high_motion, 1),   make_discrete(high_wave, 2),   make_gamma(sc_high, sc_high_stddev, 3)]
    model5 = [make_gamma(low_light,low_light_stddev, 0),   make_poisson(high_motion, 1),   make_discrete(high_wave, 2),   make_gamma(sc_high, sc_high_stddev, 3)]

    model6 = [make_gamma(low_light,low_light_stddev, 0),   make_poisson(low_motion, 1),    make_discrete(low_wave, 2),    make_gamma(sc_low, sc_low_stddev, 3)]
    model7 = [make_gamma(low_light,low_light_stddev, 0),   make_poisson(no_motion, 1),    make_discrete(low_wave, 2),    make_gamma(sc_low, sc_low_stddev, 3)]
    model8 =[make_gamma(low_light,low_light_stddev, 0),    make_poisson(low_motion, 1),    make_discrete(low_wave, 2),    make_gamma(sc_high, sc_high_stddev, 3)]
    model9 = [make_gamma(high_light,ligh_stddev, 0),       make_poisson(low_motion, 1),    make_discrete(low_wave, 2),    make_gamma(sc_low, sc_low_stddev, 3)]
    
    model10 = [make_gamma(high_light,ligh_stddev, 0),       make_poisson(high_motion, 1),   make_discrete(high_wave, 2),   make_gamma(sc_high, sc_high_stddev, 3)]
    model11 = [make_gamma(low_light,low_light_stddev, 0),   make_poisson(high_motion, 1),   make_discrete(high_wave, 2),   make_gamma(sc_high, sc_high_stddev, 3)]

    
    
    models = [model0, model1, model2, model3, model4,model5, model6, model7, model8, model9, model10, model11]

    hmm = CompositeModelHMM(models, A, pi0, verbose=True)
    
    data = pull_data()
   
    all_times = []
    flat_seg = []
    packaged_info = []
    count = 0
    hmm_dict = {}
    timestring = strftime("HMM_%Y-%m-%d_%H:%M:%S")
    
    dict_filename = timestring + '.json'

    
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
            
        t, l, c, sc, energy, waves, soundmags = data_windows.data_to_windows(data[key], k_period_in_seconds)

        
        sc[where(sc < 0)] = 0.0
        sc = log(sc + 1.0) / log(2)
        #sc[where(sc > 10)] = 10
        #sc = sc.astype(int)

        waves[where(soundmags > k_sound_disturbance_threshold)] += 1
        waves[where(energy > k_energy_disturbance_threshold)] += 1
        soundmags -= 40.0
        soundmags[where(soundmags < 0)] = 0;

        waves[where(waves > 0)] = 1.0;
        l[where(l < 0)] = 0.0
        l = (log2(k_raw_light_to_lux*l * k_lux_multipler + 1.0)) + 0.1
        energy[where(energy < 0)] = 0.0
        energy /= 2000

        
        '''
        plot(t, c)
        plot(t, log(l + 10.0))
        show()
        '''
        
        for i in xrange(len(t)):
            flat_seg.append([l[i], c[i],waves[i], sc[i],energy[i],   soundmags[i]])

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


        to_proto(hmm,'-1', timestring)
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
        
        t, l, c, sc, energy, waves, soundmags = data_windows.data_to_windows(data[key], k_period_in_seconds)
        sc[where(sc < 0)] = 0.0
        sc = log(sc + 1.0) / log(2)

        #sc[where(sc > 10)] = 10
        #sc = sc.astype(int)
        
        soundmags -= 40.0
        soundmags[where(soundmags < 0)] = 0;

        waves[where(soundmags > k_sound_disturbance_threshold)] += 1
        waves[where(energy > k_energy_disturbance_threshold)] += 1
        waves[where(waves > 0)] = 1.0;

        l[where(l < 0)] = 0.0
        l = (log2(k_raw_light_to_lux*l * k_lux_multipler + 1.0)) + 0.1
        energy[where(energy < 0)] = 0.0
        energy /= 2000
        
        
        seg = []
        for i in xrange(len(t)):
            seg.append([l[i], c[i],waves[i], sc[i],energy[i],   soundmags[i]])
        
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
            plot(t2, soundmags/10.0 )
            legend(['log light', 'pill wake counts', 'log sound counts', 'energy', 'wavecount', 'sound magnitude'])
            
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
                
        
    
