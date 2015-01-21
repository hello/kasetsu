#!/usr/bin/python
import segment_all_data
from numpy import *
import json
from pylab import *

def pull_data():
    k_interval = 15.0 # minutes
    k_segment_split_duaration = 60.0 * 3.0 #minutes
    k_max_segment_length_in_intervals = 14*60/k_interval #intervals
    k_min_segment_length_in_intervals = 5*60/k_interval #intervals
    
    print ('reading file')
    f = open('mydata.json')
    data2 = json.load(f)
    f.close()
    
    print data2.keys()
    print ('segmenting')
    segments = segment_all_data.segment(data2);
    summary = segment_all_data.summarize(segments,k_interval)
    
    summary3 = segment_all_data.enforce_summary_limits(summary, k_min_segment_length_in_intervals, k_max_segment_length_in_intervals)
    
    segment_all_data.prepend_zeros(summary3, 8, 8)
    
    print ('vectorizing')
    meas, info = segment_all_data.vectorize_measurements(summary3)
    return meas, info, data2.keys()
    
if __name__ == '__main__':
    meas, info, users = pull_data()
    
    vecdict = dict((key, []) for key in users)
        

    vecs = []
    
    for k in xrange(len(meas)):
        m = meas[k]
        accnorm = m[0]
        freq = m[1]
        user = info[k][0]
        for i in xrange(len(freq)):
            if freq[i] > 0 or accnorm[i] > 0:
                v = [freq[i], accnorm[i]]
                vecdict[user].append(v)
                vecs.append(v)

        
        
    print 'plotting'
    v2 = array(vecs)
    hist2d(v2[:, 0], v2[:, 1], 5)
    show()
    
    for k in xrange(len(users)):
        key = users[k]
        v3 = array(vecdict[key])
        
        if len(v3.shape) > 1:
            hist2d(v3[:, 0], v3[:, 1], 5)
            title(key)
            show()
