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

for i in range(1):
    m = meas[i + 20]

    path, path2 = hmm.decode(m,4)

    plot(path)
    plot(path2, '.-')
    show()
