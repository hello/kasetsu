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
october_1_2014_unix_time = 1412121600.0

pill_data_filename = 'csv/pill_data_2014_12_08.csv'
light_data_filename = 'csv/light_data_2014_12_08.csv'
survey_data_filename = 'csv/sleep_survey_2014_12_19.csv'

save_filename = 'savedata_for_bayes.json'

min_count_pill_data = 250

default_energy = 0
 
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
    
    data2 = all_data.join_by_account_id(data, min_count_pill_data)
        
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
        pilldata = d[key]['pill']
        indices, mdata, counts = pill_data_to_windows(pilldata, period, min_m)
        
        hist(counts, bins=range(0, 16))
        title('n=%d,person=%s' % (len(counts), key))
        show()

    

 
