#!/usr/bin/python
import pillcsv
import sensecsv
import surveycsv
import all_data
import os.path
import json
import segment_all_data

october_1_2014_unix_time = 1412121600.0

pill_data_filename = 'csv/pill_data_2014_12_08.csv'
light_data_filename = 'csv/light_data_2014_12_08.csv'
survey_data_filename = 'csv/sleep_survey_2014_12_19.csv'

save_filename = 'foo.json'

min_count_pill_data = 250
 
bounds_in_seconds = 3600 * 2
 
def filter_data_by_survey_period(data):
    for key in data:
        pilldata = data['pill']
        sensedata = data['sense']
        surveydata = data['survey']
        
        n = len(surveydata[0])
        
        for j in xrange(n):
            bedtime_bounds = surveydata[j][0] - bounds_in_seconds;
            waketime_bounds = surveydata[j][2] + bounds_in_seconds
            
            
 
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
    pull_data()
 
