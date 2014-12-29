#!/usr/bin/python

import json
from numpy import *
import hmm.discrete.MultipleDiscrete

import all_data
import segment_all_data
from pylab import *

hmm = hmm.discrete.MultipleDiscrete.MultipleDiscreteHMM()

f = open('alldata.json','r')
alldata = json.load(f)
f.close()

joined = all_data.join_by_account_id(alldata,250)
meas = segment_all_data.process(joined)

hmm.load_from_file('model2.json')

for i in range(100):
    m = meas[i + 0]
    
    paths = hmm.decode(m,4)
    print 'found %d paths' % len(paths)
    q = 1.0
    print paths.values()
    for path in paths:
        plot(array(path)*q)
        q = q - 0.01
    
    show()
