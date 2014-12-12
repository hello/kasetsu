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

k_conversion_factor = (1.0 / 1000.0 / 60.0) # to minutes from milliseconds
k_interval = 6.0 # minutes
k_segment_split_duaration = 60.0 * 3.0 #minutes
k_max_segment_length_in_intervals = 60*3 #intervals
k_min_segment_length_in_intervals = 15*3 #intervals

k_num_zeros_to_prepend = 10

def flatten(days_of_data):
    events = []
    for day in days_of_data:
        for item in day:
            events.append(item)
            
    #sort ascending by time        
    sorted_events = sorted(events, key=lambda k: k[key_time]) 
    
    return sorted_events

def filter_bad_values(events):
    events2 = [item for item in events if item[key_value] > 0]
    
    return events2

'''
    take list of events, find gaps of time in events, and use those gaps 
    to split the events into segments of events where there is activity
'''
def segment(events):
    t1_list = []
    t2_list = []
    
    if len(events) == 0:
        return None
        
    times = [event[key_time] for event in events]
    seg_t1 = events[0][key_time]
    t1 = seg_t1
    last_t2 = t1
    
    for event in events:
      
        t2 = event[key_time]
        dt = float(t2-t1)*k_conversion_factor
        
        if dt > k_segment_split_duaration:
            seg_t2 = last_t1
            t1_list.append(seg_t1)
            t2_list.append(seg_t2)

            seg_t1 = t2
            
        last_t1 = t1
        t1 = t2

    segments = []
    
    for i in range(len(t1_list)):
        t1 = t1_list[i]
        t2 = t2_list[i]
        
        i1 = bisect(times, t1)
        i2 = bisect(times, t2)  + 1
                
        segments.append(events[i1:i2])
        
    return segments


'''
    build series of observation data at fixed intervals for training HMMs

'''

def summarize(segments, interval_in_minutes):
    if segments is None or len(segments) == 0:
        return None
       
    summary = []
    for segment in segments:
        times = [int(item[key_time]) for item in segment]
        
        if times is None or len(times) == 0:
            continue
            
        t0 = times[0]
    
        #get time in minutes from first
        times = [(t - t0) * k_conversion_factor for t in times ]
        indices = [int(t / interval_in_minutes) for t in times]  

        maxidx = indices[-1]
        mycounts = []
        myenergies = []
        for i in range(maxidx+1):
            mycounts.append(0) 
            myenergies.append(0)
            
            
        for i in range(len(indices)):
            idx = indices[i]
            mycounts[idx] = mycounts[idx] + 1
            myenergies[idx] = myenergies[idx] + segment[i][key_value]
    
        
        for i in range(len(myenergies)):
            #transform energy output to to a quantized log value
            logval = int(numpy.ceil(numpy.log10(myenergies[i] + 1.0) + 1))
            myenergies[i] = logval
        
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
            continue
            
        #reject
        if len(counts) > max_length:
            continue
            
        
        summary2.append({key_counts : counts,  key_energies : energies})
        
    return summary2
    
def prepend_zeros(summary, numzeros):
        for item in summary:
            counts = item[key_counts]
            energies = item[key_energies]
            
            item[key_counts] = numpy.concatenate((numpy.zeros((numzeros, )), counts))
            item[key_energies] = numpy.concatenate((numpy.zeros((numzeros, )), energies))

    
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
        
            

def process(jsondata):
    events = flatten(jsondata)
    events2 = filter_bad_values(events)
    
    segments2 = segment(events2)
    summary = summarize(segments2,k_interval)

    summary2 = enforce_summary_limits(summary, k_min_segment_length_in_intervals, k_max_segment_length_in_intervals)

    prepend_zeros(summary2, k_num_zeros_to_prepend)

    meas = vectorize_measurements(summary2)
    return meas
    
    
if __name__ == '__main__':
    f = open(sys.argv[1])
    data = json.load(f)
    f.close()
    
    summary2 = process(data)
    f = open(sys.argv[1] + '.summary', 'w')
    json.dump(summary2, f)
    f.close()
