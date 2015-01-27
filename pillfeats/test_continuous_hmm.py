#!/usr/bin/python
import pillcsv
import sensecsv
import surveycsv
import all_data
import os.path
import json
from numpy import *
from pylab import *
import sklearn.mixture
import sys
from hmm.continuous.PoissonHMM import PoissonHMM
from time import strftime



save_filename = 'savedata.json'

k_min_count_pill_data = 250
k_min_date = '2015-01-01'
k_min_m_val = 4.0

k_default_energy = 50

k_period_in_seconds = 15 * 60.0
k_segment_spacing_in_seconds = 120 * 60.0
k_min_segment_length_in_seconds = 240*60.0
k_segment_padding_in_seconds = 180 * 60.0
 
def pull_data():
    import dbdata
    import os.path
    d = dbdata.DataGetter('benjo','benjo','localhost')
    
    if os.path.isfile(save_filename):
        d.load(save_filename)
    else:
        d.do_all(k_min_count_pill_data, k_min_date)
        d.save(save_filename)

    return d.data

def pill_data_to_windows(pilldata, period_in_seconds, min_m_val):
    t = array(pilldata[0]).copy().astype(int)
    m = array(pilldata[1]).copy()
    
    indices = t / int(period_in_seconds)
    #indices -= indices[0]
    
    unique_indices = unique(indices)
    
    N = len(unique_indices)
    energies = zeros((N, ))
    counts = zeros((N, ))
    
    datadict = {}
    
    for ut in unique_indices:
        datadict[ut] = [0, 0]
    
    for i in xrange(len(indices)):
        idx = indices[i]
        mval = m[i]
        
        if mval < min_m_val:
            continue
        
        datadict[idx][0] += k_default_energy
        datadict[idx][0] += mval
        datadict[idx][1] += 1
        
        
    indices2 = []
    maccumulation = []
    counts = []

    for key in sorted(datadict.keys()):
        val = datadict[key]
        indices2.append(key)
        maccumulation.append(val[0])
        counts.append(val[1])
        
    
    return (indices2,maccumulation, counts)
    
    
    
def windows_to_segments(indices2,counts, period_in_seconds, segment_spacing_in_seconds, min_segment_length_in_seconds, segment_padding_in_seconds):
    diff_in_seconds = diff(indices2) * period_in_seconds
    segment_idx = where(diff_in_seconds > segment_spacing_in_seconds)[0]

    output_times = []
    output_segments = []
    
    npad = int(segment_padding_in_seconds / period_in_seconds)

    for i in xrange(len(segment_idx) - 1):
        idx1 = segment_idx[i] + 1
        idx2 = segment_idx[i+1]
        
        i1 = indices2[idx1]
        i2 = indices2[idx2]

        dt = (i2 - i1) * period_in_seconds
        
        if dt < min_segment_length_in_seconds:
            continue
    
        segment_len = i2 - i1 + 1
        segment = zeros((segment_len, ))
        times = array(range(i1-npad, i2+1+npad)) 
        times += 1
        times *= period_in_seconds

        for iseg in xrange(idx1, idx2+1):
            seg_idx = indices2[iseg] - i1
            segment[seg_idx] = counts[iseg]
            
        
        z = zeros((npad, ))
    
        s2 = concatenate((z, array(segment), z))
       
        output_times.append(array(times))
        output_segments.append(s2)
        
    return output_times, output_segments
        
if __name__ == '__main__':
    set_printoptions(precision=3, suppress=True, threshold=np.nan)
    nargs = len(sys.argv)
    d = pull_data()
   
    all_times = []
    all_segments = []
    packaged_info = []
    for key in d:
        pilldata = d[key]['pill']
        indices, mdata, counts = pill_data_to_windows(pilldata, k_period_in_seconds, k_min_m_val)
        times,segments = windows_to_segments(indices,counts, k_period_in_seconds, k_segment_spacing_in_seconds, k_min_segment_length_in_seconds, k_segment_padding_in_seconds)
        
        if 1:

            for seg in segments:
                packaged_info.append((key, seg))
        
            all_times.extend(times)
            all_segments.extend(segments)
        
    '''
    A = array([[0.8, 0.2, 1e-6], 
                [0.1, 0.8, 0.1], 
               [1e-6, 0.2, 0.8]]) 
               
    '''
               
    A = array([[0.8, 0.15,0.05], 
                [0.001, 0.8, 0.199], 
                [0, 0.1, 0.9]]) 
             
               
    pi0 = array([0.95, 0.05, 0.05])
        
    means = [0.1, 6.0, 2.0]
    weights = [0.7, 1.0, 1.0]
    
    hmm = PoissonHMM(3,A,pi0, means, weights, verbose=True )
    
    flat_seg = []
    for seg in all_segments:
        flat_seg.extend(seg)
        
    save('flat_seg', flat_seg)


    hmm.train(flat_seg, 10)
    
    filename = strftime("HMM_%Y-%m-%d_%H:%M:%S.json")
    print ('saving to %s' % filename)

    f = open(filename, 'w')
    json.dump(hmm.to_dict(), f)
    f.close()
    print hmm.A
    print hmm.thetas
 
    
    for info in packaged_info:
        seg = info[1]
        key = info[0]
        path = hmm.decode(seg)
        plot(path, '.-')
        plot(seg)
        title(key)
        show()
    

    
        
    
