#!/usr/bin/python
from numpy import *
import time


def data_to_windows(data,  period_in_seconds):

    t = array(data[0])    
    
    light = array(data[1])
    sounds = array(data[2])
    soundmag = array(data[3])
    m = array(data[4])
    w = array(data[5])
    offset = array(data[6])
    t += offset
    
    last_idx = t[0] / period_in_seconds;
    
    out_times = []
    out_counts = []
    out_sounds = []
    out_light = []
    out_energy = []
    out_waves = []
    out_soundmag = []
    count = 0
    pill_count = 0
    lv = 0
    scount = 0
    energy = 0
    waves = 0
    soundmag_max = 0  
    for i in xrange(len(data[0])):
        idx = int(t[i] / period_in_seconds)
        
        if m[i] != None and m[i] != -1:
            pill_count += 1
            if m[i] > energy:
                energy = m[i]
                
        
        if soundmag[i] > soundmag_max:
            soundmag_max = soundmag[i]
            
            
        count += 1
        waves += w[i]
        lv += light[i]
        scount += sounds[i]
        
        if idx != last_idx:
            foo = 4
            out_times.append(t[i])
            out_light.append(lv / count)
            out_counts.append(pill_count)
            out_sounds.append(scount)
            out_energy.append(energy)
            out_waves.append(waves)
            out_soundmag.append(soundmag_max)
            count = 0
            pill_count = 0
            lv = 0
            scount = 0
            energy = 0
            waves = 0;
            soundmag_max = 0
            
        last_idx = idx

        
    
    return (array(out_times),array(out_light), array(out_counts), array(out_sounds), array(out_energy), array(out_waves), array(out_soundmag))
    
    
def windows_to_segments(times,lights, counts, period_in_seconds, segment_spacing_in_seconds, min_segment_length_in_seconds, segment_padding_in_seconds):
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
 
