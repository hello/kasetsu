#!/usr/bin/python
import pillcsv
import sensecsv
import surveycsv
import all_data
import os.path
import json
from numpy import *
from pylab import *
import sys
import scipy.stats
save_filename = 'savedata2.json'

min_count_pill_data = 250
min_date = '2015-01-01'

default_energy = 0
 

def get_pill_and_sense_events(data):
    pilldata = array(data['pill'])
    lightdata = array(data['sense'])
    t1 = pilldata[0].copy().astype(int)
    t2 = lightdata[0].copy().astype(int)
    x1 = pilldata[0].copy()
    x2 = lightdata[1] - lightdata[2]
    
    pd2 = [t1, x1]
    ld2 = [t2, x2]
    return (pd2, ld2)
    
def data_to_windows(data,  period_in_seconds, min_m_val = None):
    t = array(data[0]).copy().astype(int)
    m = array(data[1]).copy()
    
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
        
        if min_m_val is not None and mval < min_m_val:
            continue
        
        datadict[idx][0] += default_energy
        datadict[idx][0] += mval
        datadict[idx][1] += 1
        
    
    badkeys = []
    for key in datadict:
        if datadict[key][1] == 0:
            badkeys.append(key)

    for key in badkeys:
        del datadict[key]
        
    indices2 = []
    maccumulation = []
    counts = []

    for key in sorted(datadict.keys()):
        val = datadict[key]
        indices2.append(key)
        
        
        tot_energy = val[0]
        #if val[1] > 0:
        #    avg_energy /= val[1]
        
        maccumulation.append(tot_energy)
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
    
    
MIN_LOG_PROB = log(0.001)

stm = matrix([[1.0, 0.0], 
             [0.0, 1.0]])

means = [9.33529384, 2.56768044]
lp_no_motion = log(array([0.7, 0.3]))
def bayes(seg):
    n = len(seg)
    
    lp = array([log(0.95), log(0.05)])
    
    probs = zeros((n, 2))
    psns = []
    psns.append(scipy.stats.poisson(means[0]))
    psns.append(scipy.stats.poisson(means[1]))

    for i in xrange(n):
        meas = seg[i]
        
        if meas > 0:
            lik = [psns[0].pmf(meas), psns[1].pmf(meas)] 
            loglik = log(array(lik))
            lp += loglik
        
        else:
            lp += lp_no_motion

        lp -= amax(lp)
        lp[where(lp < MIN_LOG_PROB)] = MIN_LOG_PROB

        
        p = exp(lp)
        p /= sum(p)
        p = stm * matrix(p).transpose()
        p = p.reshape(2, )
        
        lp = array(log(p))
        probs[i] = p
        
    return probs
    
def pull_data():
    import dbdata
    import os.path
    d = dbdata.DataGetter('ben1','benjo','localhost')
    
    if os.path.isfile(save_filename):
        d.load(save_filename)
    else:
        d.do_all(min_count_pill_data, min_date)
        d.save(save_filename)

    return d.data
    

if __name__ == '__main__':
    set_printoptions(precision=3, suppress=True, threshold=np.nan)
    max_dt = 180 #minutes
    min_m = 10.0
    period = 15 * 60.0
    segspace = 180 * 60.0
    minseglen = 240 * 60.0
    segpad = 240*60.0


    
    d = pull_data()
    
    
    
    
    mm = []
    cts = []
    for key in d:
        pilldata, lightdata = get_pill_and_sense_events(d[key])
        indices, mdata, counts = data_to_windows(pilldata, period, min_m)
        indices2, ldata, counts2 = data_to_windows(lightdata, period)
        
        pill_times, pill_segments = windows_to_segments(indices, counts, period, segspace, minseglen, segpad)

        #if key == 'benejoseph@gmail.com':
        if 1:
            for kseg in xrange(len(pill_times)):
                t = pill_times[kseg]
                md = pill_segments[kseg]
                probs = bayes(md)
                
                tt = array(t)/3600.0
                plot(tt, md, '.-', tt, probs[:, 1])
                title('%s %d' % (key, kseg))
                show()
        
        #aggregate
        mm.extend(mdata)
        cts.extend(counts)
        
        '''
        figure(1)
        ax = subplot(2, 1, 1)
        plot(indices, mdata, '.-')
        title(key)
        grid('on')
        subplot(2, 1, 2, sharex=ax)
        plot(indices, counts, '.-')
        grid('on')
        show()
        '''
        
    mm = array(mm)


    

 
