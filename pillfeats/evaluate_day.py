#!/usr/bin/python
import sys

import extract_pill_data
import pillcsv
from pylab import *
from numpy import *
import json
from hmm.discrete.MultipleDiscrete import MultipleDiscreteHMM

def plot_data(x, m, day):
   
    numhours = sum([f == 2 for f in x[20:-20]]) / 4.0
    t = array(range(len(m[0])))/4.0
    plot(t, x, 'k.-')
    plot(t, m[0])
    plot(t, m[1])
    title('DATA SET %s, %f hours in mode 2' % (day, numhours))
    legend(['state', 'energies', 'num times woken'])

import segment_pill_data
if __name__ == '__main__':
    set_printoptions(precision=3, suppress=True, threshold=np.nan)

    auth = sys.argv[1]
    date = sys.argv[2]
    hmm_file = sys.argv[3]
    
    data = extract_pill_data.get_info_for_day_from_server(auth, date)
    
    #{"account_id": 773, "timestamp": 1416025200000, 
    #"timezone_offset": -28800000, "value": 10224, "tracker_id": 738, "id": 550748}
    
    timelist = []
    valuelist = []
    for item in data:
        if item['value'] > 0:
            timelist.append(item['timestamp']/1000.0)
            valuelist.append(item['value'])
        
    
    datadict = {'day1' : [timelist, valuelist]}
    pillcsv.sort_pill_data(datadict)
    
    segs = segment_pill_data.process(datadict)
    
    f = open(hmm_file, 'r')
    hmm_data = json.load(f)
    f.close()
    
    A = array(hmm_data['A'])
    print A
    pi = array(hmm_data['pi'])
    print pi
    obsmodels = hmm_data['obsmodels']
    
    hmm = MultipleDiscreteHMM(A, pi)
    
    for obsmodel in obsmodels:
        print array(obsmodel)
        hmm.addModel(array(obsmodel))
        
    for seg in segs:
        path = hmm.decode(seg)
        
        plot_data(path, seg, date)
        show()
    
    
    
    
