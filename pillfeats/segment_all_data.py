#!/usr/bin/python
from bisect import *
from copy import *
import sys
import json
import numpy
from pylab import *


key_time = 'timestamp'
key_value = 'value'
key_counts = 'counts'
key_energies = 'energies'
key_lightvar = 'lightvariance'

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
        pilllists = dict_of_lists[key]['pill']
        senselist = dict_of_lists[key]['sense']

        timelist = pilllists[0]
        valuelist = pilllists[1]
        
        sensetimes = senselist[0]
        temperatures = senselist[1]
        humidities = senselist[2]
        lights = senselist[3]
        
    
        t1_list = []
        t2_list = []
    
        if len(timelist) == 0:
            continue
            
        seg_t1 = timelist[0]
        t1 = seg_t1
        last_t2 = t1
        
        is_one_segment_found = False

        for t in timelist:
          
            t2 = t
            dt = float(t2-t1)*k_conversion_factor
            
            if dt > k_segment_split_duaration:
                seg_t2 = last_t1
                t1_list.append(seg_t1)
                t2_list.append(seg_t2)
                seg_t1 = t2
                
                is_one_segment_found = True
                
            last_t1 = t1
            t1 = t2
            
        if not is_one_segment_found:
            seg_t2 = last_t1
            t1_list.append(seg_t1)
            t2_list.append(seg_t2)
            seg_t1 = t2
            
    
        
        for i in range(len(t1_list)):
            segment_dict = {}
            
            t1 = t1_list[i]
            t2 = t2_list[i]
            
            i1 = bisect(timelist, t1)
            i2 = bisect(timelist, t2)  + 1
            
            segment_dict['pill'] = (timelist[i1:i2], valuelist[i1:i2])

            
            j1 = bisect(sensetimes, t1)
            j2 = bisect(sensetimes, t2)  + 1


            segment_dict['sense'] = (sensetimes[j1:j2],temperatures[j1:j2],humidities[j1:j2],lights[j1:j2])
            
            segments.append(segment_dict)

      
    return segments


'''
    build series of observation data at fixed intervals for training HMMs
'''

def compute_log_variance(x, logbase = 2.0, offset=1.0):
    return numpy.log(numpy.var(x) + offset) / numpy.log(logbase)
    
def compute_log_range(x, logbase = 2.0, maxval=10.):
    min = numpy.amin(x)
    max = numpy.amax(x)
    med = numpy.median(x)
    range = max - min
    fracchange = range / (min + 20)
    fracchange = fracchange - 0.5
    
    if fracchange < 0:
        fracchange = 0
    
    val =  numpy.ceil(numpy.log(fracchange + 1) / numpy.log(logbase))
    
    if val > maxval:
        val = maxval
    
    return val

def summarize(segments, interval_in_minutes):
    if segments is None or len(segments) == 0:
        return None
       
    summary = []
    for segment in segments:
        times = segment['pill'][0]
        values = segment['pill'][1]
        
        sensetimes = segment['sense'][0]
        humidities = segment['sense'][1]
        temperatures = segment['sense'][2]
        lights = segment['sense'][3]
        
        if times is None or len(times) == 0:
            continue
            
        t0 = times[0]
        
        #get time in minutes from first
        times = [(t - t0) * k_conversion_factor for t in times ]
        sensetimes = [(t - t0) * k_conversion_factor for t in sensetimes]

        #get index of each time point
        indices = [int(t / interval_in_minutes) for t in times]  
        indices2 = [int(t / interval_in_minutes) for t in sensetimes]  

        if len(indices2) == 0 or len(indices) == 0:
            continue

        if indices2[-1] > indices[-1]:
            maxidx = indices2[-1]
        else:
            maxidx = indices[-1]

        mycounts = []
        myenergies = []
        mylight = []
        
        #create counts and energies arrays
        for i in xrange(maxidx+1):
            mycounts.append(0) 
            myenergies.append(0)
            mylight.append(0)
            
            
        #SUMMARIZE PILL DATA
        for i in xrange(len(indices)):
            idx = indices[i]
            mycounts[idx] = mycounts[idx] + 1
            myenergies[idx] = myenergies[idx] + values[i]
    
        for i in range(len(myenergies)):
            #transform energy output to to a quantized log value
            logval = int(numpy.ceil(numpy.log10(myenergies[i] + 1.0) ))
            myenergies[i] = logval
            
        for i in range(len(mycounts)):
            logval = int(numpy.ceil(numpy.log(mycounts[i] + 1.0)/numpy.log(2.0) ))
            mycounts[i] = logval
            

        #SUMMARIZE SENSE DATA
        for idx in xrange(maxidx+1):
            indices = [i for i in xrange(len(indices2)) if indices2[i] == idx]

            lightvals = numpy.array(map(lights.__getitem__, indices))
            if len(lightvals) == 0:
                lightvals = numpy.array([0])
                
            y = int(compute_log_range(lightvals, 3, 6))
            
            mylight[idx] = y

        
        summary.append({key_counts : mycounts,  key_energies : myenergies,  key_lightvar : mylight})
        
    return summary
    
'''
    remove segments that are too long or too short
    those that are in the acceptable range, pad with zeros to fill out
    the max length
'''
def enforce_summary_limits(summary, min_length, max_length):
    summary2 = []
    
    if summary is None:
        print 'got a nonexistant summary. wat?'
        return None
    
    for item in summary:
        counts = item[key_counts]
        
        #reject
        if len(counts) < min_length:
            #print "rejecting %d length item, which was less than %d counts" % (len(counts), min_length)
            continue
            
        #reject
        if len(counts) > max_length:
            #print "rejecting %d length item, which was greater than %d counts" % (len(counts), max_length)
            continue
            
        summary2.append(deepcopy(item))
        
    return summary2
    
def prepend_zeros(summary, numzeros, numzeros2):
        for item in summary:
            for key in item:
                thisvector = item[key]
                
                item[key] = numpy.concatenate((numpy.zeros((numzeros, )), thisvector, numpy.zeros((numzeros2, ))))
           
    
def vectorize_measurements(summary):
    meas = []
    for item in summary:
        e = item[key_energies]
        c = item[key_counts]
        l = item[key_lightvar]
        
        if len(e) != len(c):
            print ("somehow, energies and counts are not the same length.")
            continue
        
        arr = numpy.array([e, c, l])
                
        meas.append(arr)
        
    return meas
        
            

def process(dict_of_lists):
    
    segments = segment(dict_of_lists)
    
    summary = summarize(segments,k_interval)

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
