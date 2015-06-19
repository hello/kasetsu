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
from hmm.continuous.CompositeModelHMM import CompositeModelHMM


# Set the default color cycle
mpl.rcParams['axes.color_cycle'] = ['b', 'g', 'r','c','m','y','k','grey']




k_natural_light_filter_start_time = 16 #hour in 24 hours
k_natural_light_filter_stop_time = 4 #hour in 24 hours
k_sound_disturbance_threshold = 90.0
k_energy_disturbance_threshold = 18000
k_enable_interval_search = True
k_raw_light_to_lux = 1.0
k_lux_multipler = 4.0

k_reliability_threshold = 0.6
k_enter_sleep_threshold = 0.80
k_leave_sleep_threshold = k_enter_sleep_threshold - 0.05
k_min_prob = 5e-2
k_max_gap = 12 * 1.5
    

def get_unix_time_as_datetime(unix_time):
    return datetime.datetime.utcfromtimestamp(unix_time)
    
def get_unix_time_as_string(unix_time): 
    return get_unix_time_as_datetime(unix_time).isoformat(' ')   


def join_segments(sleep_segments):
    segs = []
    N = len(sleep_segments)
    t = 0

    if N == 0:
        return []

    seg1 = sleep_segments[0]

    if len(seg1) == 1:
        return []

    
    last_joined = False

    while True:

        if t + 1 < N:
            seg2 = sleep_segments[t + 1]

        if len(seg2) == 1:
            break
            
            diff = seg2[0] - seg1[1]

            if diff < k_max_gap:
                seg1[1] = seg2[1]
                last_joined = True
            else:
                segs.append(copy.deepcopy(seg1))
                last_joined = False
                seg1 = seg2

        else:

            if not last_joined:
                segs.append(copy.deepcopy(seg1))

            break
        
        t += 1

    return segs

                        

def pull_data(params, user, date,num_days): 
 
    user_list = [user]
            
    a = serverdata.BinnedDataGetter(user_list,params)

    data = a.get_all_binned_data(date,num_days)
    
    #only save if no date specified
    if date == None:
        f = open(save_filename, 'w')
        json.dump(data, f)
        f.close()


    return data

def two_state_bayes(prior,conditional):
    notprior = 1.0 - prior
    notconditional = 1.0 - conditional

    joints = [conditional * prior, notconditional * notprior]
    prob_of_data = joints[0] + joints[1]
    newprob = joints[0] / prob_of_data
    return newprob

def get_sleep_wake_from_probs(probs):
    sleep = False
    N = len(probs)
    segments = []
    for t in xrange(N):
        p = probs[t]

        if p > k_enter_sleep_threshold and not sleep:
            sleep = True
            segments.append([])
            segments[-1].append(t)

        if p < k_leave_sleep_threshold and sleep:
            sleep = False
            segments[-1].append(t)

    return segments

        

def decode_probs(paths,condprobs):
    forward_probs = []
    backward_probs = []

    T = len(paths[0])
    num_models = len(paths)

    c = []

               
            
    p = 0.05 #initial prior

    for t in xrange(T):
        for imodel in xrange(num_models):
            cond = condprobs[imodel]
            
            newp = two_state_bayes(p,cond[t])
        
 
            if newp < k_min_prob:
                newp = k_min_prob

            if newp > 1.0 - k_min_prob:
                newp = 1.0 - k_min_prob

            p = newp


        forward_probs.append(newp)
        backward_probs.append(0.0)
    
    p = 0.05 #prior

    for t in range(len(path) - 1,-1,-1):
        for imodel in xrange(num_models):
            cond = condprobs[imodel]
            
            newp = two_state_bayes(p,cond[t])
        
            if newp < k_min_prob:
                newp = k_min_prob

            if newp > 1.0 - k_min_prob:
                newp = 1.0 - k_min_prob

            p = newp

        backward_probs[t] = p


    probs = []
    for t in range(len(path)):
        #NOT joint of not sleeping forwards and not sleeping backwards
        union_of_sleep = 1.0 - (1.0 - forward_probs[t]) * (1.0 - backward_probs[t])
#        union_of_sleep = forward_probs[t] * backward_probs[t]
        
 
        probs.append(union_of_sleep)

    segments = get_sleep_wake_from_probs(probs)
    
    return probs,segments,forward_probs,backward_probs

def get_data(filename,num_days,startidx):
    x = np.loadtxt(filename,delimiter=',')
    if len(x.shape) == 1:
        x = x.reshape((x.shape[0],1))
        
    i1 = startidx*24*12
    i2 = i1 + num_days*24*12
    x = x[i1:i2,:]
    
    return {-1 : {'data' : x ,'times' : np.array(range(x.shape[0]))}}


if __name__ == '__main__':
    set_printoptions(precision=3, suppress=True, threshold=nan)
    parser = argparse.ArgumentParser()
    parser.add_argument("-m1",  "--model1", help="model file (usually a .json)",required=True)
    parser.add_argument("-m2",  "--model2", help="model file (usually a .json)")
    parser.add_argument("-m3",  "--model3", help="model file (usually a .json)")
    parser.add_argument("-u",  "--user", help="particular user to train on / evaluate, otherwise we do all users in database")
    parser.add_argument('--date', help = 'target date')
    parser.add_argument('-n','--numdays', help = 'target date',type=int,default = 1)
    parser.add_argument('-p','--probname',help = 'name of target conditional probabilities',default='p_state_given_sleep')
    parser.add_argument('-i','--input',help = 'input file name, if we are not getting from server')
    parser.add_argument('--start',help='start index when decoding file',type=int,default=0)
    args = parser.parse_args()
    set_printoptions(precision=3, suppress=True, threshold=nan)

    if args.input == None and (args.date == None or args.user == None):
        print 'you must specify input file or date/user combination'
        sys.exit(0)

    if args.input != None and (args.date != None or args.user != None):
        print 'you must specify input file OR date/user combination, but not both'
        sys.exit(0)

    params = {}

    params['natural_light_filter_start_hour'] = k_natural_light_filter_start_time
    params['natural_light_filter_stop_hour'] = k_natural_light_filter_stop_time
    params['audio_disturbance_threshold_db'] = k_sound_disturbance_threshold
    params['pill_magnitude_disturbance_threshold_lsb'] = k_energy_disturbance_threshold
    params['users'] = '-1'
    params['enable_interval_search'] = k_enable_interval_search
    

    hmms = []


    params_list = []
    #if a model was specified, load it
    f = open(args.model1, 'r')
    hmm_dict = json.load(f)
    f.close()
    hmm = CompositeModelHMM()

    hmm.from_dict(hmm_dict['default'])
    params = hmm_dict['default']['params']

    hmms.append(hmm)
    params_list.append(params)

    if args.model2 != None:
        f = open(args.model2, 'r')
        hmm_dict = json.load(f)
        f.close()
        hmm = CompositeModelHMM()
        hmm.from_dict(hmm_dict['default'])
        hmms.append(hmm)
        params_list.append(hmm_dict['default']['params'])

    if args.model3 != None:
        f = open(args.model3, 'r')
        hmm_dict = json.load(f)
        f.close()
        hmm = CompositeModelHMM()
        hmm.from_dict(hmm_dict['default'])
        hmms.append(hmm)
        params_list.append(hmm_dict['default']['params'])
 
    print 'USING MEASUREMENT PERIOD OF %d MINUTES' % params['meas_period_minutes']

    #get the data
    if args.input != None:
        data = get_data(args.input,args.numdays,args.start)
        args.user = -1
    else:
        data = pull_data(params, args.user, args.date,args.numdays)
   
    all_times = []
    flat_seg = []
    packaged_info = []
    count = 0
    hmm_dict = {}
    timestring = strftime("HMM_%Y-%m-%d_%H:%M:%S")


    #if user is specified, deal with that
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
        
     
        binnedata = data[key]['data']
        t = data[key]['times']
        
        flat_seg.extend(binnedata)
        
        indiv_user_sensor_data[key] = t, array(binnedata)

        count += 1
        
        #if count > 4:
        #    break;
       
        
    flat_seg = array(flat_seg) 
    
    #path decode / plotting
    paths = []
    prob_mappings = []
    
    for key in keys:
        
        #get sensor data for user
        t, seg = indiv_user_sensor_data[key]

        for imodel in range(len(hmms)):
            params = params_list[imodel]
            hmm = hmms[imodel]

            
            print 'MODEL %d' % (imodel)
            print hmm.A
            print hmm.get_status()
            #print seg.transpose().tolist()
            path, reliability = hmm.decode(seg)
            paths.append(path)
            cprobs = params[args.probname]
            cnds = [cprobs[s] for s in path]
            prob_mappings.append(cnds)

           


        smoothed_probs,sleep_segments,forward_probs,backward_probs = decode_probs(paths,prob_mappings)
        #print np.array(smoothed_probs).tolist()
        joined_segments = join_segments(sleep_segments)
        
        nplots = 3

        t2 = array([get_unix_time_as_datetime(tt) for tt in t])
        figure(1)
        ax = subplot(nplots, 1, 1)

        N = seg.shape[1]
        for i in xrange(N):
            plot(t2, seg[:, i])


        legend(sensor_data_names)

        #title("userid=%s, %d periods > %f, model cost=%f" % (str(key), score, limit, model_cost))
        title("userid=%s" % (str(key)))
        grid('on')
        path = paths[0]
        ax2 = subplot(nplots, 1, 2, sharex=ax)
        ax2.fmt_xdata = mdates.DateFormatter('%Y-%m-%d | %H:%M')
        ax.fmt_xdata = mdates.DateFormatter('%Y-%m-%d | %H:%M:')
        questionable_indices = where(reliability < k_reliability_threshold)
        t2_marked = t2[questionable_indices]
        path_marked = path[questionable_indices]
        if args.model2 != None:
            plot(t2, path, '.-',t2,paths[1],'.-')
        else:
            plot(t2, path, '.-')

        legend(['motion','light'])
        #plot(t2, path_cost, 'ro')
        grid('on')

        ax3 = subplot(nplots,1,3,sharex=ax)
        ax3.fmt_xdata = mdates.DateFormatter('%Y-%m-%d | %H:%M')
#        plot(t2,forward_probs,t2,backward_probs,t2,smoothed_probs,'k')
#        legend(['forward','backward','smoothed'])
        plot(t2,smoothed_probs,'k-')
        legend('sleep prob')

        grid('on')

        for seg in joined_segments:
            if len(seg) < 2:
                continue
            
            if seg[0] < 0 or seg[0] >= len(t2):
                print 'seg[0] is outside of bounds'
                continue

            if seg[1] < 0 or seg[1] >= len(t2):
                print 'seg[1] is outside of bounds'
                continue
            
            start_time = t2[seg[0]]
            end_time = t2[seg[1]]

            print start_time,end_time


        show()

       
                
        
    
