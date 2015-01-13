#!/usr/bin/python
import pillcsv
import sensecsv
import surveycsv
import all_data
import os.path
import json
import segment_all_data
import myhmm
from pylab import *

october_1_2014_unix_time = 1412121600.0

pill_data_filename = 'csv/pill_data_2014_12_08.csv'
light_data_filename = 'csv/light_data_2014_12_08.csv'
survey_data_filename = 'csv/sleep_survey_2014_12_19.csv'

save_filename = 'savedata.json'

min_count_pill_data = 250
 
bounds_in_seconds = 3600 * 2

k_interval = 15.0 # minutes
k_segment_split_duaration = 60.0 * 3.0 #minutes
k_max_segment_length_in_intervals = 14*60/k_interval #intervals
k_min_segment_length_in_intervals = 5*60/k_interval #intervals

k_num_zeros_to_prepend = 20
k_num_zeros_to_append = 20
 
 
def pull_data():
    
    if not os.path.isfile(save_filename):
        print 'loading data from csv'
        survey_dict = surveycsv.read_survey_data(survey_data_filename,october_1_2014_unix_time )
        pill_dict = pillcsv.read_pill_csv(pill_data_filename,october_1_2014_unix_time)
        sense_dict = sensecsv.read_sense_csv(light_data_filename, october_1_2014_unix_time)
        
        
        valid_keys = set.intersection(set(survey_dict.keys()),set(pill_dict.keys()), set(sense_dict.keys()) )
        print len(valid_keys)
        survey_dict2 = {key : survey_dict[key] for key in valid_keys }
        pill_dict2 = {key : pill_dict[key] for key in valid_keys }
        sense_dict2 = {key : sense_dict[key] for key in valid_keys }
        
        data = {'survey' : survey_dict2,  'pill' : pill_dict2,  'sense' : sense_dict2}
        
        f = open(save_filename, 'w')
        json.dump(data, f)
        f.close()
    else:
        print 'loading data from %s' % save_filename
        f = open(save_filename)
        data = json.load(f)
        f.close()
    
    data2 = all_data.join_by_account_id(data, min_count_pill_data)
        
    for key in data2:
        data2[key]['survey'] = data['survey'][key]
    
    return data2

if __name__ == '__main__':
    dict_of_lists = pull_data()
    
    '''
    for key in dict_of_lists:
        if dict_of_lists[key].has_key('survey'):
            s = dict_of_lists[key]['survey']
            n = len(s[0])
            for i in xrange(n):
                print 'yooo', (s[2][i] - s[0][i]) / 3600
    '''
    
    segments = segment_all_data.segment(dict_of_lists)
    
    summary = segment_all_data.summarize(segments,k_interval)

    segment_all_data.get_labels(summary, dict_of_lists)
    
    summary2 = []
    for s in summary:
        if s.has_key('label'):
            label = s['label']
            interval = s['interval']
            
            if label[0] > 4.0: #if dt overlap is greater than 4 hours
                summary2.append(s)
                
    
    summary3 = segment_all_data.enforce_summary_limits(summary2, k_min_segment_length_in_intervals, k_max_segment_length_in_intervals)
    
    segment_all_data.prepend_zeros(summary3, k_num_zeros_to_prepend, k_num_zeros_to_append)

    meas, info = segment_all_data.vectorize_measurements(summary3)
    
    hmm = myhmm.MyHmm()
    for i in xrange(len(meas)):
        m = meas[i]
        user, interval, label = info[i]
        
        if label != None:
            t1 = label[1] - interval[0] 
            t2 = label[2] - interval[0] 
            t3 = label[3] - interval[0]
            t1 = t1 / 60.0 / k_interval
            t2 = t2 / 60.0 / k_interval
            t3 = t3 / 60.0 / k_interval
            t1 += k_num_zeros_to_prepend
            t2 += k_num_zeros_to_prepend
            t3 += k_num_zeros_to_prepend
            
        
        path, liks = hmm.decode(m, k_num_zeros_to_prepend, 1.0)
        
        hrs_slept = sum(path == 2) / 4.0
        
        if True:
            
            figure(1)
            subplot(3, 1, 1)
            title('slept %d hours' % hrs_slept)

            for lik in liks:
                plot(lik)
                
                
            if label != None:
                plot(t1, 0.001, 'k.')
                plot(t2, 0.001, 'ko')
                plot(t3, 0.001, 'ko')

                
            legend(['off bed', 'on bed', 'sleep'])
            grid('on')
            
            subplot(3, 1, 2)
            plot(path)
            grid('on')
            
            
            subplot(3, 1, 3)
            t = range(len(m[0]))
            plot(t, m[0])
            plot(t, m[1])
            plot(t, m[2])
            
            show()
            

 
