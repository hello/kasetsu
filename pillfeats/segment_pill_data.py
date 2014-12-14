#!/usr/bin/python
from bisect import *
from copy import *
import sys
import json
import numpy
key_time = 'timestamp'
key_value = 'value'
key_counts = 'counts'
key_energies = 'energies'

k_conversion_factor = (1.0  / 60.0) # to minutes from seconds
k_interval = 15.0 # minutes
k_segment_split_duaration = 60.0 * 3.0 #minutes
k_max_segment_length_in_intervals = 14*60/k_interval #intervals
k_min_segment_length_in_intervals = 4*60/k_interval #intervals

k_num_zeros_to_prepend = 20
k_num_zeros_to_append = 20



def filter_bad_values(events):
    events2 = [item for item in events if item[key_value] > 0]
    
    return events2

'''
    take list of events, find gaps of time in events, and use those gaps 
    to split the events into segments of events where there is activity
'''
def segment(dict_of_lists):
    segments = []

    for key in dict_of_lists:
        lists = dict_of_lists[key]
        timelist = lists[0]
        valuelist = lists[1]
    
        t1_list = []
        t2_list = []
    
        if len(timelist) == 0:
            continue
            
        seg_t1 = timelist[0]
        t1 = seg_t1
        last_t2 = t1
        
        for t in timelist:
          
            t2 = t
            dt = float(t2-t1)*k_conversion_factor
            
            if dt > k_segment_split_duaration:
                seg_t2 = last_t1
                t1_list.append(seg_t1)
                t2_list.append(seg_t2)
    
                seg_t1 = t2
                
            last_t1 = t1
            t1 = t2
    
        
        for i in range(len(t1_list)):
            t1 = t1_list[i]
            t2 = t2_list[i]
            
            i1 = bisect(timelist, t1)
            i2 = bisect(timelist, t2)  + 1
                    
            segments.append((timelist[i1:i2], valuelist[i1:i2]))
            
    return segments


'''
    build series of observation data at fixed intervals for training HMMs

'''

def summarize(segments, interval_in_minutes):
    if segments is None or len(segments) == 0:
        return None
       
    summary = []
    for segment in segments:
        times = segment[0]
        values = segment[1]
        
        if times is None or len(times) == 0:
            continue
            
        t0 = times[0]
        
        #get time in minutes from first
        times = [(t - t0) * k_conversion_factor for t in times ]

        #get index of each time point
        indices = [int(t / interval_in_minutes) for t in times]  

        maxidx = indices[-1]
        mycounts = []
        myenergies = []
        
        #create counts and energies arrays
        for i in xrange(maxidx+1):
            mycounts.append(0) 
            myenergies.append(0)
            
            
        for i in xrange(len(indices)):
            idx = indices[i]
            mycounts[idx] = mycounts[idx] + 1
            myenergies[idx] = myenergies[idx] + values[i]
    
        for i in range(len(myenergies)):
            #transform energy output to to a quantized log value
            logval = int(numpy.ceil(numpy.log10(myenergies[i] + 1.0) ))
            myenergies[i] = logval
            
        for i in range(len(mycounts)):
            logval = int(numpy.ceil(numpy.log2(mycounts[i] + 1.0) ))
            mycounts[i] = logval

        
        summary.append({key_counts : mycounts,  key_energies : myenergies})
        
        
    return summary
    
'''
    remove segments that are too long or too short
    those that are in the acceptable range, pad with zeros to fill out
    the max length
'''
def enforce_summary_limits(summary, min_length, max_length):
    summary2 = []
    
    for item in summary:
        counts = copy(item[key_counts])
        energies = copy(item[key_energies])
        
        #reject
        if len(counts) < min_length:
            #print "rejecting %d length item, which was less than %d counts" % (len(counts), min_length)
            continue
            
        #reject
        if len(counts) > max_length:
            #print "rejecting %d length item, which was greater than %d counts" % (len(counts), max_length)
            continue
            
        
        summary2.append({key_counts : counts,  key_energies : energies})
        
    return summary2
    
def prepend_zeros(summary, numzeros, numzeros2):
        for item in summary:
            counts = item[key_counts]
            energies = item[key_energies]
            
            item[key_counts] = numpy.concatenate((numpy.zeros((numzeros, )), counts, numpy.zeros((numzeros2, ))))
            item[key_energies] = numpy.concatenate((numpy.zeros((numzeros, )), energies, numpy.zeros((numzeros2, ))))

    
def vectorize_measurements(summary):
    meas = []
    for item in summary:
        e = item[key_energies]
        c = item[key_counts]
        
        if len(e) != len(c):
            print ("somehow, energies and counts are not the same length.")
            continue
        
        arr = numpy.array([e, c])
                
        meas.append(arr)
        
    return meas
        
            

def process(dict_of_lists):
    
    segments2 = segment(dict_of_lists)
    
    summary = summarize(segments2,k_interval)

    summary2 = enforce_summary_limits(summary, k_min_segment_length_in_intervals, k_max_segment_length_in_intervals)

    prepend_zeros(summary2, k_num_zeros_to_prepend, k_num_zeros_to_append)

    meas = vectorize_measurements(summary2)
    return meas
    
    
if __name__ == '__main__':
    f = open(sys.argv[1])
    data = json.load(f)
    f.close()
    
    meas = process(data)
    f = open(sys.argv[1] + '.meas', 'w')
    json.dump(summary2, f)
    f.close()
