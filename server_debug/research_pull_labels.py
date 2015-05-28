#!/usr/bin/python

import sys
import datetime
import requests
import numpy as np
import time
import json

k_uri = 'http://ec2-52-1-32-223.compute-1.amazonaws.com/v1/prediction/sleep_events/{}/{}'
k_magic_auth = '7.e0aa1ca0289449f5b3b3c257da9523ec'

def get_time_as_string(timestamp,offset):
    t = datetime.datetime.utcfromtimestamp(( offset + timestamp)/1000)
    return t.strftime('%Y-%m-%d %H:%M:%S')

num_days = 1
start_date_string = sys.argv[1]
user_id = int(sys.argv[2])
#num_days = 10
#start_date_string = '2015-02-18'
k_algorithm = 'hmm'
k_algorithm2 = 'sleep_score'

k_params = {'algorithm' : k_algorithm2}

def pull_date_for_user(userid):
    responses = []
    
    if userid is not None:
        
        headers = {'Authorization' : 'Bearer %s' % k_magic_auth}
        
        mydate = datetime.datetime.strptime(start_date_string, '%Y-%m-%d')
    
        for iday in range(num_days):
            datestring = mydate.strftime("%Y-%m-%d")
            
            mydate += datetime.timedelta(days=1)
            url = k_uri.format(userid,datestring)
            print url
            response = requests.get(url,params=k_params,headers = headers)
            if not response.ok:
                print 'fail with %d on %s ' % (response.status_code,datestring)
                continue
   
            data = response.json()
            
            if len(data) == 0:
                print 'no responses found on %s' % datestring

            responses.append(data)
         
       
        
    return responses

def print_results(data):
    
    for item in data:
        for mydict in item:
            
            event_type = mydict['type']
            timestr = get_time_as_string(mydict['startTimestamp'],mydict['timezoneOffset'])
               
            print timestr,event_type
            
        print '\n'
                
if __name__ == '__main__':
    if sys.argv[3] == 'hmm':
        k_params['algorithm'] = 'hmm'
        
    resp = pull_date_for_user(user_id)
    print_results(resp)

