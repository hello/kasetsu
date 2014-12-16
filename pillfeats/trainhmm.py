#!/usr/bin/python

import segment_pill_data
import json
from numpy import *
from numpy.random import *
from hmm.discrete.MultipleDiscrete import MultipleDiscreteHMM
from pylab import *
import sys
import pillcsv
from time import strftime


data_file = 'pill_data_2014_12_08.csv'
min_unix_time = 1414800000.0 #November 1, 2014
NUM_ITERS = 10
            

if __name__ == '__main__':
    set_printoptions(precision=3, suppress=True, threshold=np.nan)
    
    pilldata = pillcsv.read_pill_csv(data_file, min_unix_time)
    pillcsv.sort_pill_data(pilldata)
        
    meas = segment_pill_data.process(pilldata)
    
    maxenergy = int(amax(array([amax(m[0, :]) for m in meas])))
    maxcounts = int(amax(array([amax(m[1, :]) for m in meas])))

    print 'max energy %d' % maxenergy
    print 'max counts %d' % maxcounts

    #state0 = not on bed
    #state1 = on bed not sleeping
    #state2 = on bed sleeping
    N  = 3 #number of states
    
    A = array([[0.8, 0.2, 0.00001], 
              [0.05, 0.35, 0.6], 
              [0.00001, 0.001, 0.999],])
              

    B1 = zeros((N, maxenergy + 1))
    B1[0,0] = 1.0 #NOT on bed, no energy (index1) is all this state can be
    B1[1, 0:] = 1.0 #disturbed movement, cannot be zero energy
    B1[2, :] = array(range(maxenergy+1, 0, -1)) #on bed--some other distribution, higher probability of lower energy

 
    
    B2 = zeros((N, int(maxcounts + 1)))
    B2[0, 0] = 1.0
    B2[1, 0:] = 1.0
    B2[2, :] = array(range(maxcounts+1, 0, -1))    

  
    
    x = array([0.9,0.05 , 0.05])
    '''
    B1 = array([[ 1.   ,  0.   ,  0.   ,  0.   ,  0.   ,  0.   ,  0.   ,  0.   ,0.   ,  0.   ,  0.   ,  0.   ],
       [ 0.   ,  0.   ,  0.001,  0.021,  0.036,  0.022,  0.004,  0.609,0.175,  0.065,  0.065,  0.001],
       [ 0.448,  0.001,  0.011,  0.141,  0.259,  0.06 ,  0.   ,  0.   , 0.   ,  0.066,  0.014,  0.   ]])
       
    B2 = array([[ 1.   ,  0.   ,  0.   ,  0.   ,  0.   ,  0.   ],
       [ 0.   ,  0.   ,  0.056,  0.07 ,  0.871,  0.002],
       [ 0.624,  0.18 ,  0.145,  0.05 ,  0.001,  0.   ]])

    A  = array( 
    [[ 0.969 ,  0.031 ,  1e-6 ], 
    [ 0.05 ,   0.896 ,  0.055], 
    [ 1e-6   ,   0.012 ,  0.988]])
    '''
    #make rows sum to one
    row_sums = A.sum(axis=1)
    A = A / row_sums[:, newaxis]

    row_sums = B1.sum(axis=1)
    B1 = B1 / row_sums[:, newaxis]

    row_sums = B2.sum(axis=1)
    B2 = B2 / row_sums[:, newaxis]
    
    x = array([ 0.998 ,  0.001, 0.001])
    
    print A
    print B1
    print B2
    
    hmm2 = MultipleDiscreteHMM(A,x)
    hmm2.addModel(B1)
    hmm2.addModel(B2)
    
  
    '''  
    testmeas = zeros((2, 100))
    
    testmeas[0][20] = 5
    testmeas[1][20] = 6
    
    
    testmeas[0][90] = 5
    testmeas[1][90] = 5
    
    testmeas[0][40:42] = 1
    testmeas[0][40:42] = 1
    
    n = 45
    
    testmeas[0][n:n+2] = 1
    testmeas[0][n:n+2] = 1
    
    print hmm2.decode(testmeas)
    plot(hmm2.decode(meas[34]))
    plot(meas[34][0])
    plot(meas[34][1])

    print [amin(m[0]) for m in meas]

    show()

    '''
    
#   '''
    print "training on %d segments" % len(meas)
    
    hmm2.train(meas, NUM_ITERS)
    #hmm2.force_no_zero_values(1e-9)
    
    result = {}
    result['A'] = hmm2.A.tolist()
    result['obsmodels'] = []
    for model in hmm2.obsmodels:
        result['obsmodels'].append(model.tolist())
        
    result['pi'] = hmm2.pi.tolist()
    
    print hmm2.A
    for model in hmm2.obsmodels:
        print model
        
    print hmm2.pi


    f = open(strftime("HMM_%Y-%m-%d_%H:%M:%S.json"), 'w')
    json.dump(result, f)
    f.close()
    
    for imeas in xrange(len(meas)):
        m = meas[imeas]
        x = hmm2.decode(m)
        numhours = sum([f == 2 for f in x[20:-20]]) / 4.0
        t = array(range(len(m[0])))/4.0
        #print len(t),len(x), len(m[0]), len(m[1])
        plot(t, x, 'k.-')
        plot(t, m[0])
        plot(t, m[1])
        title('DATA SET %d, %f hours in mode 2' % (imeas, numhours))
        legend(['state', 'energies', 'num times woken'])
        

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
    
    
