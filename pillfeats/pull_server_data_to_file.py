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

                        

def pull_data(params, user_list, date,num_days): 
             
    a = serverdata.BinnedDataGetter(user_list,params)

    data = a.get_all_binned_data(date,num_days)
    
    #only save if no date specified
    if date == None:
        f = open(save_filename, 'w')
        json.dump(data, f)
        f.close()


    return data




if __name__ == '__main__':
    set_printoptions(precision=3, suppress=True, threshold=nan)
    parser = argparse.ArgumentParser()
    parser.add_argument('--date', help = 'target date', required=True)
    parser.add_argument('-n','--numdays',default=1, help = 'num days to retrieve')
    parser.add_argument('-o','--outfile', required=True)
    parser.add_argument('-u','--user',default=None)
    parser.add_argument('--skipunpartnered',action='store_true',default=False,help='skip users that do not have a partner')
    parser.add_argument('--userlistfile',help='list of user account ids where the first column is the account_id')
    args = parser.parse_args()

    if (args.userlistfile == None and args.user == None) or (args.userlistfile and args.user):
        print 'you must specify either a user list file or a user'
        sys.exit(0)


    params = {}

    params['natural_light_filter_start_hour'] = k_natural_light_filter_start_time
    params['natural_light_filter_stop_hour'] = k_natural_light_filter_stop_time
    params['audio_disturbance_threshold_db'] = k_sound_disturbance_threshold
    params['pill_magnitude_disturbance_threshold_lsb'] = k_energy_disturbance_threshold
    params['users'] = '-1'
    params['enable_interval_search'] = k_enable_interval_search
    params['meas_period_minutes'] = 5

    user_list = []

    if args.userlistfile != None:
        with open(args.userlistfile, 'rb') as csvfile:
            reader = csv.reader(csvfile, delimiter=',')

            for row in reader:
                user_list.append(row[0])

    else:
        user_list = [args.user]
        
    
    data = pull_data(params, user_list, args.date,args.numdays)
  
    f = open(args.outfile,'wb')
    json.dump(data,f)
    f.close()

    print 'wrote to %s' % (args.outfile) 
        
    
