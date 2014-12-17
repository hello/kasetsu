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
import argparse
import extract_last_week


data_file = 'alldata.json'
min_unix_time = 1414800000.0 #November 1, 2014
NUM_ITERS = 10
            
def evaluate(hmm2, meas):
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

    
    
def initialize_model(meas):
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
    
    return hmm2
    
    
if __name__ == '__main__':
    
    parser = argparse.ArgumentParser()
    parser.add_argument("-f", "--file", help="specify input source from file",type=str)
    parser.add_argument("-t", "--token", help="specify input from server via token",type=str)
    parser.add_argument("-a",  "--action",help="evaluate,train", required=True, type=str)
    parser.add_argument("-m",  "--model", help="model file (usually a .json)")
    parser.add_argument("--iter", help="number of training iterations")
    args = parser.parse_args()
    
    if args.file is None and args.token is None:
        print "must specify either token (-t) or file (-f)"
        sys.exit(0)
    
    set_printoptions(precision=3, suppress=True, threshold=np.nan)

    
    if args.action == 'evaluate' and args.model == None:
        print "you must specify a model file (-m) if you are going to evaluate"
        sys.exit(0)
   
    if args.file is not None and args.token is not None:
        print "you can not specify both a input file or a server auth token"
        sys.exit(0)

        
    if args.model is not None:
        isModelInitialized = True
        
        hmm2 = MultipleDiscreteHMM()
        hmm2.load_from_file(args.model)
        
    if args.iter is not None:
        NUM_ITERS = int(args.iter)
    
        
        

    if args.token is not None:
        alldata = extract_last_week.get_week_info()
        joined = all_data.join_by_account_id(alldata,1)
        meas = segment_all_data.process(joined)

        
    elif args.file is not None:
        #get data
        f = open(data_file, 'r');
        alldata = json.load(f)
        f.close()
        
        joined = all_data.join_by_account_id(alldata,250)
        meas = segment_all_data.process(joined)
    
    
    
            
    if args.action == 'train':
    
        if not isModelInitialized:
            hmm2 = initialize_model(meas)
    
        
      
        print "training on %d segments" % len(meas)
        
        hmm2.train(meas, NUM_ITERS)
        
        filename = strftime("HMM_%Y-%m-%d_%H:%M:%S.json")
        
        hmm2.save_to_file(filename)
        
    elif args.action == 'evaluate':
        evaluate(hmm2, meas)
 


    
    
