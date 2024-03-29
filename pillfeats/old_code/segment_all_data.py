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

key_id = 'id'
key_survey = 'survey'
key_interval = 'interval'
key_label = 'label'

k_sensor_keys = [key_lightvar, key_counts, key_energies]


k_conversion_factor = (1.0  / 60.0) # to minutes from seconds
k_interval = 15.0 # minutes
k_segment_split_duaration = 60.0 * 3.0 #minutes
k_max_segment_length_in_intervals = 14*60/k_interval #intervals
k_min_segment_length_in_intervals = 5*60/k_interval #intervals

k_num_zeros_to_prepend = 6
k_num_zeros_to_append = 6

#hour 0-23, mode 0 - not sleepy times
#mode 1 - possibly sleepy times
#mode 2 - definitely sleep times

k_hour_mode_lookup = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23]


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
            dt = seg_t2 - seg_t1
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
            
            segment_dict[key_id] = key
            
            segments.append(segment_dict)

      
    return segments


'''
    build series of observation data at fixed intervals for training HMMs
'''

def compute_log_variance(x, logbase = 2.0, offset=1.0):
    return numpy.log(numpy.var(x) + offset) / numpy.log(logbase)
    
def compute_log_range(x, logbase = 2.0, maxval=10.):
    imin = numpy.argmin(x)
    imax = numpy.argmax(x)
    
    min = x[imin]
    max = x[imax]
        
    #if the max happened later than the min, then this was an increase
    #we only are looking at lights out
    if imax > imin:
        range = 0
    else:
        range = max - min
    
    fracchange = range / (min + 20)
    fracchange = fracchange - 0.25
    
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
        id = segment[key_id]
        
        sensetimes = segment['sense'][0]
        humidities = segment['sense'][1]
        temperatures = segment['sense'][2]
        lights = segment['sense'][3]
        
        if times is None or len(times) == 0:
            continue
            
        t0 = times[0]
        tf = times[-1]
        
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
        mytimeofday = []
        
        #create counts and energies arrays
        for i in xrange(maxidx+1):
            mycounts.append(0) 
            myenergies.append(0)
            mylight.append(0)
            mytimeofday.append(0)
            
            
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
            
        for i in range(len(mytimeofday)):
            tt = t0 + interval_in_minutes*i*60
            mytimeofday[i] = k_hour_mode_lookup[datetime.datetime.fromtimestamp(tt).hour] 
             

        #SUMMARIZE SENSE DATA
        for idx in xrange(maxidx+1):
            indices = [i for i in xrange(len(indices2)) if indices2[i] == idx]

            lightvals = numpy.array(map(lights.__getitem__, indices))
            if len(lightvals) == 0:
                lightvals = numpy.array([0])
                
            y = int(compute_log_range(lightvals, 3, 1.))
            
            mylight[idx] = y

        
        summary.append({key_counts : mycounts,  key_energies : myenergies,  key_lightvar : mylight, key_id : id,  key_interval : (t0, tf)})
        
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
                if key in k_sensor_keys:
                    thisvector = item[key]                
                    item[key] = numpy.concatenate((numpy.zeros((numzeros, )), thisvector, numpy.zeros((numzeros2, ))))
           
    
def vectorize_measurements(summary):
    meas = []
    info = []
    for item in summary:
        e = item[key_energies]
        c = item[key_counts]
        l = item[key_lightvar]
        id = item[key_id]
        interval = item[key_interval]
        
        label = None
        if item.has_key(key_label):
            label = item[key_label]
        
            
        
        if len(e) != len(c):
            print ("somehow, energies and counts are not the same length.")
            continue
        
        arr = numpy.array([e, c, l])
                
        meas.append(arr)
        info.append((id,interval,label))
        
    return meas, info
        
            
def get_labels(summary, dict_of_lists):

    for id in dict_of_lists:
        if not dict_of_lists[id].has_key(key_survey):
            continue
            
        survey = dict_of_lists[id][key_survey]

        #assume it's all sorted
        matching_summaries = [s for s in summary if s[key_id] == id]
        
        if len(matching_summaries) == 0:
            continue
        
        label_idx = 0
        summary_idx = 0
        N = len(survey[0])
        while(summary_idx < len(matching_summaries) and label_idx < N):
            
            s = matching_summaries[summary_idx]
            
            t0_1 = s[key_interval][0]
            tf_1 = s[key_interval][1]
            
            t0_2 = survey[0][label_idx]
            tf_2 = survey[2][label_idx]
            oof = t0_1
            #print t0_1 - oof, (tf_1 -oof)/3600.0, (t0_2 - oof) / 3600.0, (tf_2 -oof)/3600.0
            #end of segment 1 less than beginning of segment 2? move up segment 1
            if tf_1 < t0_2:
                #print 'continue 1'
                summary_idx = summary_idx + 1
                continue
                
            
            #beginning of segment 1 greater than end of segment2?  move up segment 2
            if t0_1 > tf_2:
                #print 'idx++'
                label_idx = label_idx + 1
                continue
                    
            #neither end of seg1 < begin seg2 nor 
            #        end of seg2 < begin of seg1
            # overlap!
            
            if t0_1 > t0_2:
                tt1 = t0_1
            else:
                tt1 = t0_2
                
            if tf_1 < tf_2:
                tt2 = tf_1
            else:
                tt2 = tf_2
                
            dt = tt2 - tt1
            print 'dt overlap (hrs):', dt / 3600.0
            s[key_label] = [dt, survey[0][label_idx], survey[1][label_idx], survey[2][label_idx]]
                
            summary_idx += 1
            #label_idx += 1
            
            
        
    #for d in 
    #if dict_of_lists.has_key('')
    foo = 3

def process(dict_of_lists):
    
    segments = segment(dict_of_lists)
    
    summary = summarize(segments,k_interval)

    get_labels(summary, dict_of_lists)

    summary2 = enforce_summary_limits(summary, k_min_segment_length_in_intervals, k_max_segment_length_in_intervals)

    prepend_zeros(summary2, k_num_zeros_to_prepend, k_num_zeros_to_append)

    meas, info = vectorize_measurements(summary2)
    
    return meas
    
    
if __name__ == '__main__':
    f = open(sys.argv[1])
    data = json.load(f)
    f.close()
    
    meas = process(data)
    f = open(sys.argv[1] + '.meas', 'w')
    json.dump(summary2, f)
    f.close()
