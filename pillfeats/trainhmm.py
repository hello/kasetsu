#!/usr/bin/python

import segment_all_data
import json
from numpy import *
from numpy.random import *
from hmm.discrete.MultipleDiscrete import MultipleDiscreteHMM
from pylab import *
import sys
import pillcsv
from time import strftime
import all_data

data_file = 'alldata.json'
min_unix_time = 1414800000.0 #November 1, 2014
NUM_ITERS = 10
            

if __name__ == '__main__':
    set_printoptions(precision=3, suppress=True, threshold=np.nan)

    task = 'evaluate'
    if len(sys.argv) > 1:
        task = sys.argv[1]
        
    isModelInitialized = False
    if len(sys.argv) > 2:
        isModelInitialized = True
        f = open(sys.argv[2], 'r')
        hmmdata = json.load(f)
        f.close()
        
        hmm2 = MultipleDiscreteHMM(array(hmmdata['A']),array(hmmdata['pi']))
        
        for B in hmmdata['obsmodels']:
            B = array(B)
            hmm2.addModel(B)
            
    if len(sys.argv) > 3:
        NUM_ITERS = int(sys.argv[3])
    
        
    f = open(data_file, 'r');
    alldata = json.load(f)
    f.close()
    
    joined = all_data.join_by_account_id(alldata,250)
    meas = segment_all_data.process(joined)
    
    
    
            
    if task == 'train':
    
        if not isModelInitialized:
            maxenergy = int(amax(array([amax(m[0, :]) for m in meas])))
            maxcounts = int(amax(array([amax(m[1, :]) for m in meas])))
            maxlight = int(amax(array([amax(m[2, :]) for m in meas])))
        
        
            print 'max energy val %d' % maxenergy
            print 'max counts val %d' % maxcounts
            print 'max light val %d' % maxlight
        
            #state0 = not on bed
            #state1 = on bed not sleeping
            #state2 = on bed sleeping
            N  = 3 #number of states
            
            A = array([[0.95, 0.05, 0.0], 
                      [0.05, 0.90, 0.05], 
                      [0.0, 0.20, 0.80],])
                      
        
            B1 = zeros((N, maxenergy + 1))
            B1[0,0] = 1.0 #NOT on bed, no energy (index1) is all this state can be
            B1[1, :] = array(range(maxenergy+1))      #disturbed movement, cannot be zero energy
            B1[2, :] = array(range(maxenergy+1, 0, -1)) #on bed--some other distribution, higher probability of lower energy
        
            B2 = zeros((N, int(maxcounts + 1)))
            B2[0, 0] = 1.0
            B2[1, :] = array(range(maxcounts+1))
            B2[2, :] = array(range(maxcounts+1, 0, -1))    
            
            B3 = zeros((N, int(maxlight + 1)))
            B3[0, :] = 1.0
            B3[1, :] = array(range(1, maxlight + 2))
            B3[2, 0] = 1.0
        
          
        
            #make rows sum to one
            row_sums = A.sum(axis=1)
            A = A / row_sums[:, newaxis]
        
            row_sums = B1.sum(axis=1)
            B1 = B1 / row_sums[:, newaxis]
        
            row_sums = B2.sum(axis=1)
            B2 = B2 / row_sums[:, newaxis]
            
            row_sums = B3.sum(axis=1)
            B3 = B3 / row_sums[:, newaxis]
            
            x = array([ 0.998 ,  0.001, 0.001])
            
            print A
            print B1
            print B2
            print B3
        
            
            hmm2 = MultipleDiscreteHMM(A,x)
            hmm2.addModel(B1)
            hmm2.addModel(B2)
            hmm2.addModel(B3)
    
        
      
        print "training on %d segments" % len(meas)
        
        hmm2.train(meas, NUM_ITERS)
        #hmm2.force_no_zero_values(1e-9)
        
        
    
#    hmm2.A[0, 2] = 1e-6
#    hmm2.A[2, 0] = 1e-6
        result = {}
        result['A'] = hmm2.A.tolist()
        result['obsmodels'] = []
        for model in hmm2.obsmodels:
            result['obsmodels'].append(model.tolist())
            
        result['pi'] = hmm2.pi.tolist()
    
        f = open(strftime("HMM_%Y-%m-%d_%H:%M:%S.json"), 'w')
        json.dump(result, f)
        f.close()
    
    print hmm2.A
    for model in hmm2.obsmodels:
        print model
        
    print hmm2.pi
    
    for imeas in xrange(len(meas)):
        m = meas[imeas]
        x = hmm2.decode(m)
        numhours = sum([f == 2 for f in x[20:-20]]) / 4.0
        t = array(range(len(m[0])))/4.0
        #print len(t),len(x), len(m[0]), len(m[1])
        plot(t, x, 'k.-')
        plot(t, m[0])
        plot(t, m[1])
        plot(t, m[2])

        title('DATA SET %d, %f hours in mode 2' % (imeas, numhours))
        legend(['state', 'energies', 'num times woken', 'log light range'])
        

        show()

#        if imeas > 10:
#            break;
#    '''

'''
    k = 0
    for seq in esequences:
        path = hmm.decode(seq)
        counts_of_sleep = sum([i == 2 for i in path])
        hours_of_sleep = counts_of_sleep / 10.0
        plot(path)
        title('sequence %d, %f hours of sleep' % (k, hours_of_sleep))
        show()
        k = k + 1
        #if k > 10:
        #    break
    
'''
    
    
