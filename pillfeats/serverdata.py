#!/usr/bin/python
import time
import requests
import datetime
import calendar
import numpy


#k_server = 'http://research-api-benjo.hello.is'
k_server = 'http://ec2-52-1-32-223.compute-1.amazonaws.com'

k_minute_data_url = k_server + '/v1/datascience/device_sensors_motion/'
k_binned_url = k_server + '/v1/datascience/binneddata/'

k_magic_auth = '7.e0aa1ca0289449f5b3b3c257da9523ec'
#k_magic_auth = '2.26d34270933b4d5e88e513b0805a0644'
k_headers = {'Authorization' : 'Bearer %s' % k_magic_auth}


def get_datestr_as_timestamp(datestr):
    mydate = datetime.datetime.strptime(datestr, '%Y-%m-%d')
    return calendar.timegm(mydate.utctimetuple())*1000

    
class BinnedDataGetter(object):
    def __init__(self, account_id_list, aux_params):
        self.account_id_list = account_id_list
        self.aux_params = aux_params
        
    def get_all_binned_data(self, from_date_str, num_days):
        t0 = get_datestr_as_timestamp(from_date_str)
        mydict = {}
        for account_id in self.account_id_list:
            ret_data = self.get_data_for_user(t0, account_id, num_days)
            
            if ret_data is not None:
                mydict[account_id] = ret_data
                
        return mydict
                
        
    def get_data_for_user(self, from_time, account_id, num_days):

        ts = "%d" % from_time
        params = {  'from_ts' : ts,  
                    'account_id' : str(account_id),  
                    'num_days' : num_days, 
                    'pill_threshold_counts' : self.aux_params['pill_magnitude_disturbance_threshold_lsb'], 
                    'sound_threshold_db' : self.aux_params['audio_disturbance_threshold_db'], 
                    'nat_light_start_hour' : self.aux_params['natural_light_filter_start_hour'], 
                    'nat_light_stop_hour' : self.aux_params['natural_light_filter_stop_hour'],
                    'kickoff_count_threshold' : self.aux_params['kickoff_count_threshold'],
                    'duration_threshold' : self.aux_params['duration_threshold'], 
                    'meas_period' : 15
                    }
        
       
        
        d = None
        response = requests.get(k_binned_url,params=params,headers=k_headers)
        
        if not response.ok:
            print 'fail with %d ' % (response.status_code)
        else:
            print 'got data for user ',  account_id
            d = response.json()
            
            xvec = numpy.array(d['data']).transpose()
            tvec = numpy.array(d['ts_utc'])
            offset = d['timezone_offset_millis']
            tvec += offset
            tvec /= 1000
            
            mydict = {}
            mydict['times'] = tvec.tolist()
            mydict['data'] = xvec.tolist()
            
            return mydict
            
        return None
        
    

        
class ServerDataGetter(object):
    def __init__(self, account_id_list):
        self.account_id_list = account_id_list
        
    def get_all_minute_data(self, from_date_str, num_days,  min_num_records, min_num_pill_records):
        t0 = get_datestr_as_timestamp(from_date_str)
        data = []
        for account_id in self.account_id_list:
            ret_data = self.get_data_for_user(t0, account_id, num_days)
            
            if ret_data is not None:
                data.extend(ret_data)
                

        return self.get_records_as_dict_entry(data, min_num_records, min_num_pill_records)
                
            
    def get_data_for_user(self, from_time, account_id, num_days):
    
        ts = "%d" % from_time
        params = {'from_ts' : ts,  'account_id' : str(account_id),  'num_days' : num_days}
        
        d = None
        response = requests.get(k_minute_data_url,params=params,headers=k_headers)
        
        if not response.ok:
            print 'fail with %d ' % (response.status_code)
        else:
            print 'got data for user ',  account_id
            d = response.json()
            
        return d
        
    def get_records_as_dict_entry(self, data,  min_num_records, min_num_pill_records):
        '''
        [u'account_id', u'sound_num_disturbances', u'sound_peak_disturbances', u'light', u'svm_no_gravity', u'ts', u'kickoff_counts', u'motion_range', u'offset_millis', u'on_duration_seconds']
       device_sensors_master.account_id,
            device_sensors_master.ts,
            device_sensors_master.ambient_light,
            device_sensors_master.audio_num_disturbances,
            device_sensors_master.audio_peak_disturbances_db,
            tracker_motion_master.svm_no_gravity,
            device_sensors_master.wave_count
            
        '''
        
        datadict = {}
        for record in data:
            key = record['account_id']
            
            if not datadict.has_key(key):
                datadict[key] = [[], [], [], [], [], [], [], [], [], []]
                
            datadict[key][0].append(record['ts']/1000)
            datadict[key][1].append(record['offset_millis']/1000)
            datadict[key][2].append(record['light'])
            datadict[key][3].append(record['sound_num_disturbances'])
            datadict[key][4].append(record['sound_peak_disturbances'])
            datadict[key][5].append(record['svm_no_gravity'])
            datadict[key][6].append(record['wave_count'])
            datadict[key][7].append(record['motion_range'])
            datadict[key][8].append(record['on_duration_seconds'])
            datadict[key][9].append(record['kickoff_counts'])
            
        badkeys = []
        for key in datadict:
            if len(datadict[key][0]) < min_num_records:
                badkeys.append(key)
                continue
                
            pill_data = datadict[key][3]
            pill_counts = 0
            for p in pill_data:
                if p != None:
                    pill_counts += 1;
                    
            if pill_counts < min_num_pill_records:
                badkeys.append(key)
                
        for key in badkeys:
            del datadict[key]

        return datadict
            
        return datadict
    

if __name__ == '__main__':
    if 0:
        a = ServerDataGetter([1012,1040])
        mydata = a.get_all_minute_data('2015-02-16', 5, 1440 * 1, 100)
        #print mydata[1012]
    if 1:
        aux_params = {}
        aux_params['pill_magnitude_disturbance_threshold_lsb'] = 12000
        aux_params['audio_disturbance_threshold_db'] = 65.0
        aux_params['natural_light_filter_start_hour'] = 16.0
        aux_params['natural_light_filter_stop_hour'] = 4.0
        
        a = BinnedDataGetter([1012, 1001], aux_params)
        d = a.get_all_binned_data('2015-02-16', 3)
        
        print d
    
