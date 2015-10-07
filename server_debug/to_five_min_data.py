#!/usr/bin/python
import numpy as np
import json
import sys

name = sys.argv[1].split('.')[0]
f = open(sys.argv[1]);
x = json.load(f)
f.close()
N = 5

sig = []
print len(x)
for t in xrange(0,len(x),N):
    thesum = 0.0
    for i in xrange(t,t+N):
        if i < len(x):
            thesum += x[i]
        
    sig.append(thesum)

print len(sig)
np.savetxt(name + '_5min_2.csv', np.array(sig).reshape((1,len(sig))), delimiter=",")
