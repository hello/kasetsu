#!/usr/bin/python

import segment_pill_data
import json
from numpy import *
from hmm.discrete.DiscreteHMM import DiscreteHMM
k_files = ['ben.json', 'bryan.json', 'pang.json']

if __name__ == '__main__':
    energies = []
    for file in k_files:
        f = open(file, 'r')
        data = json.load(f)
        f.close()
        summary = segment_pill_data.process(data)
        
        e = [s['energies'] for s in summary]
        
        for item in e:
            energies.extend(item) 
        
    energies = array(energies)
    maxenergy = amax(energies)
    print 'max energy %d' % maxenergy
    M = maxenergy + 1 # "alphabet" size
    N  = 3 #number of states
    
    #state0 = not on bed
    #state1 = on bed not sleeping
    #state2 = on bed sleeping
    
    A = array([[0.7, 0.20, 0.10], 
              [0.1, 0.7, 0.2], 
              [0.1, 0.2, 0.7]])
              
    B = zeros((N, M))
    B[0,0] = 0.99
    B[0, 1] = 0.01
    
    B[1, 0] = 0.3
    B[1, 1] = 1.0
    B[1, 2] = 1.0
    
    B[2, :] = ones((1, M))
    B[2, 0] = 0.0
    row_sums = B.sum(axis=1)
    B = B / row_sums[:, newaxis]
    
    print B

    obs = concatenate((zeros((10, )),energies[200:400]))
    x = array([0.90, 0.05, 0.05])
    
    print x.shape
    print energies.shape
    set_printoptions(precision=4, suppress=True, threshold=nan)
    hmm = DiscreteHMM(N, M, A, B, x, init_type='user', verbose=True)
    
    hmm.train(obs, 100)
    
    print "Pi",hmm.pi
    print "A",hmm.A
    print "B", hmm.B
    
    
    
    
    
