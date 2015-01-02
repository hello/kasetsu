#!/usr/bin/python

import json
from numpy import *
import hmm.discrete.MultipleDiscrete

import all_data
import segment_all_data
from pylab import *

off_bed = 0
on_bed_not_sleeping = 1
on_bed_sleeping = 2

k_alpha = 0.1#on_bed_sleeping threshold (above this value)
k_beta = 0.8 #disturbance threshold (above this value)
k_gamma = 0.15 #off bed threshold (below this value)
k_num_periods_to_be_sleep = 4

def determine_sleep(liks):
    sleeps = logical_and(liks[on_bed_sleeping] > k_alpha, liks[on_bed_not_sleeping] < k_beta)
    sleep_count = 0
    istart = 0
    for i in xrange(len(sleeps)):
        s = sleeps[i]

        if sleep_count == 0 and s == True:
            istart = i
            
        if s == True:
            sleep_count = sleep_count + 1
        
        if s == False and sleep_count > 0:
            if sleep_count < k_num_periods_to_be_sleep:
                print ('purging %d sleep counts' % sleep_count)

                for j in range(istart, istart + sleep_count):
                    sleeps[j] = False
                    
            sleep_count = 0
            
    
    states = zeros((len(sleeps), )).astype(int)
    
    for i in xrange(len(sleeps)):
        #if you are sleeping then you are sleeping
        if sleeps[i] == True:
            states[i] = on_bed_sleeping
        else:
            #if you are not sleeping, but you are not "off bed", then you are on bed, not sleeping
            if liks[off_bed][i] < k_gamma:
                states[i] = on_bed_not_sleeping
            else:
                states[i] = off_bed
                
    return states

    
def pdf(paths):
    
    arrs = []
    numpaths = len(paths)
    path0 = paths.keys()[0]
    for i in range(3):
        arrs.append(zeros((1,len(path0))))

    for path in paths.keys():
        a = array(path)
        for i in range(3):
            v = (a == i).astype(float)
            arrs[i] = arrs[i] + v
            
        
    for i in range(3):
        arrs[i] = arrs[i] / numpaths
    
    newarrs = []
    for i in range(3):
        newarrs.append(arrs[i][0])
    
    return newarrs
        

hmm = hmm.discrete.MultipleDiscrete.MultipleDiscreteHMM()

f = open('alldata.json','r')
alldata = json.load(f)
f.close()

joined = all_data.join_by_account_id(alldata,250)
meas = segment_all_data.process(joined)

hmm.load_from_file('model2.json')

for i in range(100):
    m = meas[i + 0]
    
    paths = hmm.decode(m,20)
    print 'found %d paths' % len(paths)
    liks = pdf(paths)
    path = determine_sleep(liks)
    
    hrs_slept = sum(path == on_bed_sleeping) / 4.0
    if True:
        
        #figure(1)
        #for lik in liks:
        #    plot(lik)
        #    
        #legend(['off bed', 'on bed', 'sleep'])
        #grid('on')
        
        figure(2)
        plot(path)
        grid('on')
        title('slept %d hours' % hrs_slept)
        show()
