#!/usr/bin/python

import segment_pill_data
import json
from numpy import *
from hmm.discrete.DiscreteHMM import DiscreteHMM
from pylab import *
k_files = ['ben.json', 'bryan.json', 'pang.json']

if __name__ == '__main__':
    energies = []
    esequences = []
    for file in k_files:
        f = open(file, 'r')
        data = json.load(f)
        f.close()
        summary = segment_pill_data.process(data)
        
        e = [s['energies'] for s in summary]
        
        for item in e:
            energies.extend(item) 
            esequences.append(item)
        
    energies = array(energies)
    maxenergy = amax(energies)
    print 'max energy %d' % maxenergy
    M = maxenergy + 1 # "alphabet" size
    N  = 3 #number of states
    
    #state0 = not on bed
    #state1 = on bed not sleeping
    #state2 = on bed sleeping
    
    A = array([[0.7, 0.20, 0.0], 
              [0.2, 0.6, 0.2], 
              [0.0, 0.3, 0.7]])
              
    row_sums = A.sum(axis=1)
    A = A / row_sums[:, newaxis]
              
    B = zeros((N, M))
    B[0,0] = 0.7
    B[0, 1] = 0.3

    B[2, 0] = 0.3
    B[2, 1] = 1.0
    B[2, 2] = 1.0
    B[2, 3] = 1.0
    B[2, 4] = 0.5
    B[2, 5] = 0.1
    B[2, 6] = 0.0

    B[1, 0] = 0.1
    B[1, 1] = 0.1
    B[1, 2] = 0.2
    B[1, 3] = 0.3
    B[1, 4] = 0.4
    B[1, 5] = 0.5
    B[1, 6] = 0.7

    

    row_sums = B.sum(axis=1)
    B = B / row_sums[:, newaxis]
    
    print B

    obs = concatenate((zeros((10, )),energies))
    x = array([0.90, 0.05, 0.05])
    
    print x.shape
    print energies.shape
    set_printoptions(precision=4, suppress=True, threshold=nan)
    hmm = DiscreteHMM(N, M, A, B, x, init_type='user', verbose=True)
    
    hmm.train(obs, 4)
    
    print "Pi",hmm.pi
    print "A",hmm.A
    print "B", hmm.B
    
 #   idx = 4
#    figure(1)
#    plot(hmm.decode(obs))
#    show()

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
    
    
    
    
