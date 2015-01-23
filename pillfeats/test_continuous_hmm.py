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
from hmm.continuous.GMHMM import GMHMM

october_1_2014_unix_time = 1412121600.0

pill_data_filename = 'csv/pill_data_2014_12_08.csv'
light_data_filename = 'csv/light_data_2014_12_08.csv'
survey_data_filename = 'csv/sleep_survey_2014_12_19.csv'

save_filename = 'savedata.json'

k_min_count_pill_data = 250

k_min_m_val = 10.0


k_period_in_seconds = 15 * 60.0
k_segment_spacing_in_seconds = 180 * 60.0
k_min_segment_length_in_seconds = 240*60.0
k_segment_padding_in_seconds = 120 * 60.0
 
def pull_data():
    
    if not os.path.isfile(save_filename):
        print 'loading data from csv'
        survey_dict = surveycsv.read_survey_data(survey_data_filename,october_1_2014_unix_time )
        pill_dict = pillcsv.read_pill_csv(pill_data_filename,october_1_2014_unix_time)
        sense_dict = sensecsv.read_sense_csv(light_data_filename, october_1_2014_unix_time)
        
        
        data = {'survey' : survey_dict,  'pill' : pill_dict,  'sense' : sense_dict}
        
        f = open(save_filename, 'w')
        json.dump(data, f)
        f.close()
    else:
        print 'loading data from %s' % save_filename
        f = open(save_filename)
        data = json.load(f)
        f.close()
    
    data2 = all_data.join_by_account_id(data, k_min_count_pill_data)
        
    for key in data2:
        if data['survey'].has_key(key):
            data2[key]['survey'] = data['survey'][key]
    
    return data2


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
    
    
def windows_to_segments(indices2,maccumulation, period_in_seconds, segment_spacing_in_seconds, min_segment_length_in_seconds, segment_padding_in_seconds):
    diff_in_seconds = diff(indices2) * period_in_seconds
    segment_idx = where(diff_in_seconds > segment_spacing_in_seconds)[0]

    output_times = []
    output_segments = []

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
        times = array(range(i1, i2+1)) 
        times += 1
        times *= period_in_seconds

        for iseg in xrange(idx1, idx2+1):
            seg_idx = indices2[iseg] - i1
            segment[seg_idx] = log(maccumulation[iseg] + 1.0) # LOG LOG LOG
            
        output_times.append(array(times))
        output_segments.append(array(segment))
        
    return output_times, output_segments
        
if __name__ == '__main__':
    set_printoptions(precision=3, suppress=True, threshold=np.nan)

    d = pull_data()
   
    all_times = []
    all_segments = []
    for key in d:
        pilldata = d[key]['pill']
        indices, mdata, counts = pill_data_to_windows(pilldata, k_period_in_seconds, k_min_m_val)
        times,segments = windows_to_segments(indices,mdata, k_period_in_seconds, k_segment_spacing_in_seconds, k_min_segment_length_in_seconds, k_segment_padding_in_seconds)
        print key
        all_times.extend(times)
        all_segments.extend(segments)
        
        
    A = array([[0.8, 0.1, 0.1], 
                [0.1, 0.8, 0.1], 
               [0.1, 0.1, 0.8]]) 
             
               
    pi0 = array([0.95, 0.05, 0.5])
        
    means = array([[[0.0]], [[9.0]], [[6.0]]])
    covars = [matrix(1.0), matrix(1.0), matrix(1.0)]
    w = [[0.3333], [0.3333], [0.33333]]
    
    hmm = GMHMM(3, 1, 1, A,means,covars,w,pi0,min_std=0.1,init_type='user', verbose=True )
    
    flat_seg = []
    for seg in all_segments:
        flat_seg.extend(seg)
        
        
    hist(flat_seg, 50)
    show()
    hmm.train(flat_seg, 2)
    
    hmm.decode()
    
    print hmm.A
    print hmm.means
    print hmm.covars
    print hmm.w
    
        
    
