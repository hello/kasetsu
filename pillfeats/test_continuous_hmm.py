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


        
if __name__ == '__main__':
    set_printoptions(precision=3, suppress=True, threshold=np.nan)
    nargs = len(sys.argv)
    
    data = pull_data()
   
    all_times = []
    flat_seg = []
    packaged_info = []
    count = 0
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
    '''
    A = array([[0.8, 0.15,0.05], 
                [0.001, 0.8, 0.199], 
                [0, 0.1, 0.9]]) 
    '''
    
    #states
    # 0 - off bed (dark, no activity)
    # 1 - reading on bed (light, high activity)
    # 2 - sleep (dark, low activity)
    # 3 - tossing / turning (dark, high activity)
    # 4 - waking up (light, low activity)
    # 5 - lazy sunday (light, high activity) 
    # 6 - woke up (light, no activity)
    
    A = array([
    [0.89, 0.05, 0.05, 0.00, 0.00, 0.00, 0.01],
    [0.00, 0.80, 0.20, 0.00, 0.00, 0.00, 0.00],
    [0.00, 0.00, 0.85, 0.10, 0.05, 0.00, 0.00], 
    [0.00, 0.00, 0.50, 0.50, 0.00, 0.00, 0.00], 
    [0.00, 0.00, 0.00, 0.00, 0.90, 0.05, 0.05], 
    [0.00, 0.00, 0.00, 0.00, 0.00, 0.90, 0.10], 
    [0.10, 0.00, 0.00, 0.00, 0.00, 0.00, 0.90]

    ])
             
             
    pi0 = array([0.70, 0.05, 0.05, 0.05, 0.05, 0.05, 0.05])
        
    #light, then counts
    means = [[1.0, 6.0, 1.0, 1.0, 6.0, 6.0, 6.0],
             [0.1, 6.0, 1.0, 4.0, 1.0, 8.0, 0.1]]
    
    hmm = PoissonHMM(7,2, A,pi0, means, verbose=True )
    
    if nargs > 1:
        f = open(sys.argv[1], 'r')
        hmm.from_dict(json.load(f))
    else:
        hmm.train(flat_seg, NUMITER)
        filename = strftime("HMM_%Y-%m-%d_%H:%M:%S.json")
        print ('saving to %s' % filename)

        f = open(filename, 'w')
        json.dump(hmm.to_dict(), f)
        f.close()
    print hmm.A
    print hmm.thetas
 
    

    for key in data:
        
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
        
       
        
    
        
    
