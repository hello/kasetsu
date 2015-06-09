#!/usr/bin/python
import os.path
import json
from numpy import *
from matplotlib.pyplot import *
import sklearn.mixture
import sys
from time import strftime
import datetime
import csv
import argparse
import copy
import data_windows
import serverdata
import os.path
import initial_models
import matplotlib.dates as mdates
import matplotlib as mpl

# Set the default color cycle
mpl.rcParams['axes.color_cycle'] = ['b', 'g', 'r','c','m','y','k','grey']

#k_user_list = [1 ,  1001 ,  1002 ,  1005 ,  1012 ,  1013 ,  1025  , 1038 ,  1043    , 1052 ,  1053 ,  1060  , 1061 ,  1062 ,  1063 ,  1067 ,  1070 ,  1071 ,  1072 ,1310  , 1609 ,  1629 ,  1648]
#k_user_list2 = [1086, 1050, 1049]
#k_user_list.extend(k_user_list2)
k_user_list = [1086]
save_filename = 'savedata3.json'

k_min_count_pill_data = 0
k_min_num_days_of_sense_data = 0
k_min_date = '2015-04-26'
k_num_days_of_data = 1
k_num_days_displayed_from_single_date = 3

k_min_sleep_duration_hours = 1.5

k_natural_light_filter_start_time = 16 #hour in 24 hours
k_natural_light_filter_stop_time = 4 #hour in 24 hours
k_sound_disturbance_threshold = 90.0
k_energy_disturbance_threshold = 15000
k_enable_interval_search = True

k_reliability_threshold = 0.6


#k_raw_light_to_lux = 125.0 / (2 ** 16)
k_raw_light_to_lux = 1.0
k_lux_multipler = 4.0



forbidden_keys = []



    

def get_unix_time_as_datetime(unix_time):
    return datetime.datetime.utcfromtimestamp(unix_time)
    
def get_unix_time_as_string(unix_time): 
    return get_unix_time_as_datetime(unix_time).isoformat(' ')   

def pull_data(params, user, date): 
 
    have_valid_user_date_combo = (user != None and date != None)

    if os.path.isfile(save_filename) and not have_valid_user_date_combo: 
        print 'loading from %s' % save_filename
        f = open(save_filename, 'r')
        data = json.load(f)
        f.close()
    else:
        print 'querying DB'

        #d = dbdata.DataGetter('benjo_sensors_1','benjo','localhost')
        #data = d.get_all_minute_data(k_min_date,1440 * k_min_num_days_of_sense_data,k_min_count_pill_data)

        #d = serverdata.ServerDataGetter(k_user_list)
        #data = d.get_all_minute_data(k_min_date, k_num_days_of_data, 1440 * k_min_num_days_of_sense_data,k_min_count_pill_data)
        user_list = k_user_list
        
        if user != None:
            user_list = [user]
            
        min_date = k_min_date
        num_days = k_num_days_of_data
        
        if date != None:
            min_date = date
            num_days = k_num_days_displayed_from_single_date
            
        a = serverdata.BinnedDataGetter(user_list,params)
        data = a.get_all_binned_data(min_date,num_days)
        
        #only save if no date specified
        if date == None:
            f = open(save_filename, 'w')
            json.dump(data, f)
            f.close()


    return data


def decode_probs(path,condprobs):
    forward_probs = []
    backward_probs = []
    min_prob = 1e-2
    p = 0.05 #prior

    #forward
    for t in range(len(path)):
        state = path[t]
        p_state_given_sleep = condprobs[state]
        p_not_state_given_sleep = 1.0 - p_state_given_sleep

        joints = [p_state_given_sleep * p, p_not_state_given_sleep * (1.0 - p)]
        p_data = joints[0] + joints[1]
        p = joints[0] / p_data
 

        if p < min_prob:
            p = min_prob

        if p > 1.0 - min_prob:
            p = 1.0 - min_prob

        forward_probs.append(p)
        backward_probs.append(0.0)
    
    p = 0.05 #prior

    for t in range(len(path) - 1,-1,-1):
        state = path[t]
        p_state_given_sleep = condprobs[state]
        p_not_state_given_sleep = 1.0 - p_state_given_sleep

        joints = [p_state_given_sleep * p, p_not_state_given_sleep * (1.0 - p)]
        p_data = joints[0] + joints[1]
        p = joints[0] / p_data

        if p < min_prob:
            p = min_prob

        if p > 1.0 - min_prob:
            p = 1.0 - min_prob

        backward_probs[t] = p


    probs = []
    for t in range(len(path)):
        #NOT joint of not sleeping forwards and not sleeping backwards
        union_of_sleep = 1.0 - (1.0 - forward_probs[t]) * (1.0 - backward_probs[t])
        #NOT joint of sleeping forwards and sleeping backwards
        #union_of_not_sleep = 1.0 - (forward_probs[t] * backward_probs[t])
        #ptotal = union_of_sleep + union_of_not_sleep
        #probs.append(union_of_sleep / ptotal)
        probs.append(union_of_sleep)
        
    return forward_probs,backward_probs,probs
        

if __name__ == '__main__':
    
    parser = argparse.ArgumentParser()
    #parser.add_argument("-t",  "--train",help="evaluate,train", required=True, type=str)
    parser.add_argument("-f",  "--file", help="output file of predicted sleep / wake times")
    parser.add_argument("-m",  "--model", help="model file (usually a .json)")
    parser.add_argument("-u",  "--user", help="particular user to train on / evaluate, otherwise we do all users in database")
    parser.add_argument("--iter", type=int, help="number of training iterations", default=4)
    parser.add_argument("--adapt", action='store_true', default=False, help='compute a model for each individual user ids')
    parser.add_argument('--train', action='store_true', default=False, help='compute an aggregate model for all user ids')
    parser.add_argument('--sleeponly', action='store_true', default=False, help='only train on the sleep states')
    parser.add_argument('--initmodel', default='default', help='which initial model to choose')
    parser.add_argument('--date', help = 'optional target date, use in conjuction with a user')
    args = parser.parse_args()
    set_printoptions(precision=3, suppress=True, threshold=nan)
    
    #get initial model
    if args.initmodel == 'apnea':
        hmm, params = initial_models.get_apnea_model()
    else:
        hmm, params = initial_models.get_default_model()

    
    
 

    
    params['natural_light_filter_start_hour'] = k_natural_light_filter_start_time
    params['natural_light_filter_stop_hour'] = k_natural_light_filter_stop_time
    params['model_name'] = args.initmodel
    params['audio_disturbance_threshold_db'] = k_sound_disturbance_threshold
    params['pill_magnitude_disturbance_threshold_lsb'] = k_energy_disturbance_threshold
    params['users'] = '-1'
    params['enable_interval_search'] = k_enable_interval_search


    #if a model was specified, load it
    if args.model != None:
        f = open(args.model, 'r')
        hmm_dict = json.load(f)
        hmm.from_dict(hmm_dict['default'])
        params = hmm_dict['default']['params']
    else:
        print 'using init model %s' % args.initmodel 


    print 'USING MEASUREMENT PERIOD OF %d MINUTES' % params['meas_period_minutes']

    #get the data
    data = pull_data(params, args.user, args.date)
   
    all_times = []
    flat_seg = []
    packaged_info = []
    count = 0
    hmm_dict = {}
    timestring = strftime("HMM_%Y-%m-%d_%H:%M:%S")
    
    dict_filename = timestring + '.json'

    if args.sleeponly == True:
        trainstates = params['sleep_states']
        reestimation_obs = [1] #motion
        if args.user != None:
            dict_filename =  str(args.user) + '.json'
            params['model_name']  = 'model_for_' + str(args.user) 
    else:
        trainstates = None #do them all
        reestimation_obs = None #do them all

        
    hmm.set_reestimation_obs(reestimation_obs)

    #if user is specified, deal with that
    if args.user != None:
        print args.user
        if not data.has_key(args.user):
            print ('user does not exist in data set! quitting....')
            sys.exit(0)
        else:
            data = {args.user : data[args.user]}
    
    keys = data.keys()
    params['users'] = ','.join([("%s" % str(id)) for id in keys])

    print keys

    indiv_user_sensor_data = {}
    sensor_data_names = ['log light', 'mot.', 'disturbances', 'log soundcounts', 'art. light', 'part. mot.', 'part. dist.']
    #go through each user (the key == user number) and get their sensor data
    #append into one big sequence
    for key in data:
        
        if key in forbidden_keys:
            continue 
        
        binnedata = data[key]['data']
        t = data[key]['times']
        
        flat_seg.extend(binnedata)
        
        indiv_user_sensor_data[key] = t, array(binnedata)

        count += 1
        
        #if count > 4:
        #    break;
       
        
    flat_seg = array(flat_seg)
    print flat_seg.shape
    

    
    #if we are training, then go do it
    if args.train == True:
        print ('TRAINING')
        hmm.train(flat_seg, args.iter, trainstates)
        
        print ('saving to %s' % dict_filename)

        hmm_dict['default'] = hmm.to_dict()
        hmm_dict['default']['params'] = params

        #save to outputs
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
            myhmm.train(seg, args.iter, trainstates )
            print hmm.A

           
        
        path, reliability = myhmm.decode(seg)

        print params.keys()
        sleep_probs_forward = None
        sleep_probs_backward = None
        if params.has_key('p_state_given_sleep') and len(params['p_state_given_sleep']) > 0:
            sleep_probs_forward,sleep_probs_backward,smoothed_probs = decode_probs(path,params['p_state_given_sleep'])

        
        
        bic = myhmm.get_bic(seg, path, params['num_model_params'])
        aic = myhmm.get_aic(seg, path, params['num_model_params'])
        print "BIC is %f, AIC is %f" % (bic, aic)
        #model_cost = myhmm.forwardbackward(seg)
        #model_cost /= len(seg) / myhmm.d
        #print 'AVERAGE MODEL COST = %f' % model_cost
        #path_cost = myhmm.evaluate_path_cost(seg, path, len(seg))
        #limit = 3.0 * mean(path_cost)
        #score = sum(path_cost > limit)
        

        nplots = 2

        if sleep_probs_forward != None:
            nplots = 3
            
        if outfile == None:
            t2 = array([get_unix_time_as_datetime(tt) for tt in t])
            figure(1)
            ax = subplot(nplots, 1, 1)

            N = seg.shape[1]
            for i in xrange(N):
                plot(t2, seg[:, i])
            
            
            legend(sensor_data_names)
            
            #title("userid=%s, %d periods > %f, model cost=%f" % (str(key), score, limit, model_cost))
            title("userid=%s,bic=%f,aic=%f" % (str(key), bic, aic))
            grid('on')
            
            ax2 = subplot(nplots, 1, 2, sharex=ax)
            ax2.fmt_xdata = mdates.DateFormatter('%Y-%m-%d | %H:%M')
            ax.fmt_xdata = mdates.DateFormatter('%Y-%m-%d | %H:%M:')
            questionable_indices = where(reliability < k_reliability_threshold)
            t2_marked = t2[questionable_indices]
            path_marked = path[questionable_indices]
            plot(t2, path, 'k.-',t2_marked, path_marked, 'ro')
            legend(['path', 'possible bad decisions'])
            #plot(t2, path_cost, 'ro')
            grid('on')

            if sleep_probs_forward != None:
                 ax3 = subplot(nplots,1,3,sharex=ax)
                 ax3.fmt_xdata = mdates.DateFormatter('%Y-%m-%d | %H:%M')
                 #plot(t2,sleep_probs_forward,t2,sleep_probs_backward,t2,smoothed_probs)
                 plot(t2,smoothed_probs,'k-')
                 grid('on')
                 legend('sleep prob')

            
            show()
    
        else:
            with open(outfile, 'a') as csvfile:
                mywriter = csv.writer(csvfile, delimiter=',')
                
                for item in events:
                    row = [key]
                    row.extend(item)
                    
                    mywriter.writerow(row)
                    
            csvfile.close()
                
        
    
