#!/usr/bin/python

import segment_pill_data
import json
from numpy import *
from numpy.random import *
from hmm.discrete.DiscreteHMM import DiscreteHMM
from hmm.discrete.MultipleDiscrete import MultipleDiscreteHMM
from pylab import *
import sys

k_files = ['ben.json', 'bryan.json', 'pang.json']

NUM_ITERS = 15
            

if __name__ == '__main__':
    set_printoptions(precision=3, suppress=True, threshold=np.nan)
    meas = []
    for file in k_files:
        f = open(file, 'r')
        data = json.load(f)
        f.close()
        meas_for_file = segment_pill_data.process(data)
        meas.extend(meas_for_file)
    
    
    maxenergy = amax(array([amax(m[0, :]) for m in meas]))
    maxcounts = amax(array([amax(m[1, :]) for m in meas]))

    print 'max energy %d' % maxenergy
    print 'max counts %d' % maxcounts

    #state0 = not on bed
    #state1 = on bed not sleeping
    #state2 = on bed sleeping
    N  = 3 #number of states

    A = array([[0.90, 0.05, 0.0], 
              [0.1, 0.90, 0.1], 
              [0.0, 0.25, 0.75],])
              

    B1 = zeros((N, maxenergy + 1))
    B1[0,:] = [1.0, 0.0, 0.0, 0.0, 0.0, 0.0]
    B1[1, :] = [0.0, 1.0, 1.0, 1.0, 1.0, 1.0]
    B1[2, :] = [1.0, 1.0, 1.0, 1.0, 1.0, 1.0]

 
    
    B2 = zeros((N, int(maxcounts + 1)))
    B2[0, 0] = 1.0
    B2[1, :] = ones((maxcounts+1, ))
    B2[1, 0:2] = [0.0, 0.0]
    B2[2, 0:5] = [1.0, 1.0, 1.0, 1.0, 1.0]
    

    
    x = array([0.9,0.05 , 0.05])


    row_sums = A.sum(axis=1)
    A = A / row_sums[:, newaxis]

    row_sums = B1.sum(axis=1)
    B1 = B1 / row_sums[:, newaxis]

    row_sums = B2.sum(axis=1)
    B2 = B2 / row_sums[:, newaxis]
    
        
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
    
    
    hmm2.train(meas, NUM_ITERS)
    
    print hmm2.obsmodels
    print hmm2.A
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
    
    
