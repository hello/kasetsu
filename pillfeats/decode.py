#!/usr/bin/python

from hmm.continuous.CompositeModelHMM import CompositeModelHMM
import numpy as np
import json
import argparse
from matplotlib.pyplot import *

def get_model(filename):
    hmm = CompositeModelHMM()

    f = open(filename, 'r')
    hmm_dict = json.load(f)
    hmm.from_dict(hmm_dict['default'])

    return hmm


def get_data(filename):
    x = np.loadtxt(filename,delimiter=',')
    return x


if __name__ == '__main__':
    np.set_printoptions(precision=3, suppress=True, threshold=np.nan)

    parser = argparse.ArgumentParser()
    parser.add_argument("-m",  "--model", help="model file (usually a .json)",required=True)
    parser.add_argument("-i",  "--input", help="input data, csv",required=True)
    parser.add_argument("-n","--n", help="num data points",type=int,default=1000)
    parser.add_argument("--start",help="index to start at",type=int,default=0)
    args = parser.parse_args()

    
    hmm = get_model(args.model)
    print hmm.A
    print hmm.get_status()

    x = get_data(args.input)
    if len(x.shape) == 1:
        x = x.reshape((x.shape[0],1))

    if args.n == 0:
        args.n = x.shape[0]

    i1 = args.start
    i2 = args.start + args.n
    x2 = x[i1:i2,:]
    path,probs = hmm.decode(x2)
    #print hmm.B_map
    t = np.array(range(len(path)))
    plot(t,path,'k.-',t,x2/10.0,'b')
    grid('on')
    show()
