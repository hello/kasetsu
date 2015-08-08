#!/usr/bin/python

import sys
import datetime
import requests
import numpy as np
import time
import json
import os

#k_uri = 'http://ec2-52-1-32-223.compute-1.amazonaws.com/v1/prediction/sleep_events/{}/{}'
k_uri = 'https://research-api-benjo.hello.is/v1/prediction/sleep_events/{}/{}'
k_magic_auth = os.environ['RESEARCH_TOKEN']

def get_time_as_string(timestamp,offset):
    t = datetime.datetime.utcfromtimestamp(( offset + timestamp)/1000)
    return t.strftime('%Y-%m-%d %H:%M:%S')

num_days = 1
start_date_string = sys.argv[1]
user_id = int(sys.argv[2])

partner_filter = False
if len(sys.argv) > 4:
    if sys.argv[4] == 'yes':
        partner_filter = True

k_algorithm = 'hmm'
k_algorithm2 = 'sleep_score'

k_params = {'partner_filter' : partner_filter, 'algorithm' : k_algorithm2}

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

            if isinstance(data,dict) and data.has_key('code') and int(data['code']) == 204:
                print data['message']
                continue                  
            
            if len(data) == 0:
                print 'no responses found on %s' % datestring

            responses.append(data)
         
       
        
    return responses

def print_results(data):
    
    for item in data:
        alg_events = item['alg_events']
        feedback_events = item['feedback_events']
        
        for mydict in alg_events:
            event_type = mydict['type']
            timestr = get_time_as_string(mydict['startTimestamp'],mydict['timezoneOffset'])
            print ' PRED: ',timestr,event_type
        
        print '\n'

        for mydict in feedback_events:
            event_type = mydict['type']
            timestr = get_time_as_string(mydict['startTimestamp'],mydict['timezoneOffset'])
            print 'LABEL:', timestr,event_type

                
if __name__ == '__main__':
    k_params['algorithm'] = sys.argv[3]
 
    resp = pull_date_for_user(user_id)
    print_results(resp)

