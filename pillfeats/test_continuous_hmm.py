#!/usr/bin/python
import os.path
import json
from numpy import *
from pylab import *
import sklearn.mixture
import sys
from time import strftime
import datetime
import csv
import argparse
import copy
import data_windows
import sleep_hmm_pb2
import serverdata
import os.path
import initial_models

    
k_user_list = [1038,1085, 1050, 1052, 1053, 1070, 1071, 1012, 1013, 1043, 1025, 1061, 1060, 1049, 1062, 1067, 1005, 1063, 1001, 1]

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

k_natural_light_filter_start_time = 16 #hour in 24 hours
k_natural_light_filter_stop_time = 4 #hour in 24 hours
k_sound_disturbance_threshold = 60.0
k_energy_disturbance_threshold = 12000

#k_raw_light_to_lux = 125.0 / (2 ** 16)
k_raw_light_to_lux = 1.0
k_lux_multipler = 4.0



forbidden_keys = []


def to_proto(composite_hmm,aux_params,  user, timestring):
    print timestring
    filename = timestring + '.proto'
    
    on_bed_states = aux_params['on_bed_states']   
    sleep_states = aux_params['sleep_states']  
  
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
           
        '''
        if i in light_sleep_state:
            m_state.sleep_depth = sleep_hmm_pb2.LIGHT
        elif i in regular_sleep_state:
            m_state.sleep_depth = sleep_hmm_pb2.REGULAR
        elif i in disturbed_sleep_state:
            m_state.sleep_depth = sleep_hmm_pb2.DISTURBED
        else:
            m_state.sleep_depth = sleep_hmm_pb2.NOT_APPLICABLE
        '''
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

def get_sleep_times(t, path, params):
    events = []
    
    on_bed_states = params['on_bed_states']   
    sleep_states = params['sleep_states']  
    
    sleep_times = [0, 0]
    bed_times = [0, 0]
    
    bed_mode = mode_off_bed
    sleep_mode = mode_not_sleeping
    
    for idx in xrange(len(path)):
        state = path[idx]
        
            
        #track how long in the light sleep state
        if state not in sleep_states:
            new_sleep_mode = mode_not_sleeping
            
        if state in sleep_states:
            new_sleep_mode = mode_sleeping;

            
        #####################
        #off bed? zero out light sleep counter
        if state not in on_bed_states:
            new_bed_mode = mode_off_bed

        if state in on_bed_states:
            new_bed_mode = mode_on_bed
        
        #################################            
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
    parser.add_argument("--iter", type=int, help="number of training iterations", default=4)
    parser.add_argument("--adapt", action='store_true', default=False, help='compute a model for each individual user ids')
    parser.add_argument('--train', action='store_true', default=False, help='compute an aggregate model for all user ids')
    parser.add_argument('--saveadapt', action='store_true', default=False, help='save the adaptation for each user')
    parser.add_argument('--initmodel', default='default', help='which initial model to choose')
    args = parser.parse_args()
    set_printoptions(precision=3, suppress=True, threshold=np.nan)
    
    #get initial model
    if args.initmodel == 'apnea':
        hmm, params = initial_models.get_apnea_model()
    else:
        hmm, params = initial_models.get_default_model()

    #get the data
    data = pull_data()
   
    all_times = []
    flat_seg = []
    packaged_info = []
    count = 0
    hmm_dict = {}
    timestring = strftime("HMM_%Y-%m-%d_%H:%M:%S")
    
    dict_filename = timestring + '.json'

    #if user is specified, deal with that
    if args.user != None:
        print args.user
        if not data.has_key(args.user):
            print ('user does not exist in data set! quitting....')
            sys.exit(0)
        else:
            data = {args.user : data[args.user]}
    
    keys = data.keys()
    print keys

    indiv_user_sensor_data = {}
    sensor_data_names = ['log light', 'counts', 'disturbances', 'log soundcounts', 'art. light', 'snd mag', 'energy']
    #go through each user (the key == user number) and get their sensor data
    #append into one big sequence
    for key in data:
        
        if key in forbidden_keys:
            continue 
            
        t, l, c, sc, energy, waves, soundmags = data_windows.data_to_windows(data[key], k_period_in_seconds)

        tod = (t % 86400) / 3600.0
        non_natural_light = logical_or( (tod > k_natural_light_filter_start_time), (tod < k_natural_light_filter_stop_time)).astype(int)

        sc[where(sc < 0)] = 0.0
        sc = log(sc + 1.0) / log(2)
      
        waves[where(soundmags > k_sound_disturbance_threshold)] += 1
        waves[where(energy > k_energy_disturbance_threshold)] += 1
        soundmags -= 40.0
        soundmags[where(soundmags < 0)] = 0;
        soundmags /= 10.0

        waves[where(waves > 0)] = 1.0;
        l[where(l < 0)] = 0.0
        l = (log2(k_raw_light_to_lux*l * k_lux_multipler + 1.0)) + 0.1
        energy[where(energy < 0)] = 0.0
        energy /= 2000

        
        
        myseg = []
        for i in xrange(len(t)):
            vec = [l[i], c[i],waves[i], sc[i],non_natural_light[i], soundmags[i], energy[i]]
            flat_seg.append(vec)
            myseg.append(vec)

        indiv_user_sensor_data[key] = t, array(myseg)

        count += 1
        
        #if count > 4:
        #    break;
       
        
    flat_seg = array(flat_seg)
    print flat_seg.shape
    
    #if a model was specified, load it
    if args.model != None:
        f = open(args.model, 'r')
        hmm_dict = json.load(f)
        hmm.from_dict(hmm_dict['default'])
        params = hmm_dict['default']['params']
    
    #if we are training, then go do it
    if args.train == True:
        print ('TRAINING')
        hmm.train(flat_seg, args.iter)
        
        print ('saving to %s' % dict_filename)

        hmm_dict['default'] = hmm.to_dict()
        hmm_dict['default']['params'] = params

        #save to outputs
        to_proto(hmm,params,'-1', timestring)
        f = open(dict_filename, 'w')
        json.dump(hmm_dict, f)
        f.close()
        
    
    print hmm.A
    print hmm.get_status()
  
    
    outfile = args.file
    
    if outfile != None and os.path.isfile(outfile):
        os.remove(outfile)

    #path decode / plotting
    sleep_segments = []
    for key in keys:
        
        if key in forbidden_keys:
            continue
        
        #get sensor data for user
        t, seg = indiv_user_sensor_data[key]
        
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
        bic = myhmm.get_bic(seg, path, params['num_model_params'])
        aic = myhmm.get_aic(seg, path, params['num_model_params'])

        print "BIC is %f, AIC is %f" % (bic, aic)
        #model_cost = myhmm.forwardbackward(seg)
        #model_cost /= len(seg) / myhmm.d
        #print 'AVERAGE MODEL COST = %f' % model_cost
        #path_cost = myhmm.evaluate_path_cost(seg, path, len(seg))
        #limit = 3.0 * mean(path_cost)
        #score = sum(path_cost > limit)
        
        events = get_sleep_times(t, path, params)   

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
            
            N = seg.shape[1]
            for i in xrange(N):
                plot(t2, seg[:, i])
            
            
            legend(sensor_data_names)
            
            #title("userid=%s, %d periods > %f, model cost=%f" % (str(key), score, limit, model_cost))
            title("userid=%s,bic=%f,aic=%f" % (str(key), bic, aic))
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
                
        
    
