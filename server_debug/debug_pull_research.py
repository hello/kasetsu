#!/usr/bin/python
import datetime
import calendar
import requests
import copy
k_url = 'http://localhost:9997/v1/datascience/binneddata/'
#k_magic_auth = '7.e0aa1ca0289449f5b3b3c257da9523ec'
k_magic_auth = '2.26d34270933b4d5e88e513b0805a0644'

k_headers = {'Authorization' : 'Bearer %s' % k_magic_auth}


def get_datestr_as_timestamp(datestr):
    mydate = datetime.datetime.strptime(datestr, '%Y-%m-%d')
    return calendar.timegm(mydate.utctimetuple())*1000

def get_time_as_string(timestamp,offset):
    t = datetime.datetime.utcfromtimestamp(( offset + timestamp)/1000)
    return t.strftime('%Y-%m-%d %H:%M:%S')

num_days = 1
start_date_string = '2015-02-18'

'''

                        @QueryParam("email") String email,
                                                                    @QueryParam("account_id") Long accountId,
                                                                    @QueryParam("from_ts") Long fromTimestamp,
                                                                    @DefaultValue("3") @QueryParam("num_days") Integer numDays,
                                                                    @QueryParam("pill_threshold_counts") Double pillThreshold,
                                                                    @QueryParam("sound_threshold_db") Double soundThreshold,
                                                                    @QueryParam("nat_light_start_hour") Double naturalLightStartHour,
                                                                    @QueryParam("nat_light_stop_hour") Double naturalLightStopHour,
                                                                    @QueryParam("meas_period") Integer numMinutesInMeasPeriod
'''

k_params = {'account_id' : 1012, 
            'from_ts' : get_datestr_as_timestamp(start_date_string), 
            'num_days' : num_days, 
            'pill_threshold_counts' : 12000, 
            'sound_threshold_db' : 60, 
            'nat_light_start_hour' : 16.0, 
            'nat_light_stop_hour' : 4.0, 
            'meas_period' : 15
}

def pull_date_for_user(userid):
    responses = []
    
    if userid is not None:
        params = copy.deepcopy(k_params)
        
        params['account_id'] = userid
        headers = {'Authorization' : 'Bearer %s' % k_magic_auth}
        
        response = requests.get(k_url,params=params,headers=headers)
        
        if not response.ok:
            print 'fail with %d on %s ' % (response.status_code,'foo')
            return []

        data = response.json()
        
        return data
       

def print_results(data):
    
    for item in data:
        for mydict in item:
            
            event_type = mydict['type']
            timestr = get_time_as_string(mydict['startTimestamp'],mydict['timezoneOffset'])
               
            print timestr,event_type
            
        print '\n'
                
if __name__ == '__main__':
    pull_date_for_user(1012)

