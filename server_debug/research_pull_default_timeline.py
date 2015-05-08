#!/usr/bin/python

import sys
import datetime
import requests
import numpy as np
import time
import json


#k_uri = 'http://ec2-52-1-32-223.compute-1.amazonaws.com/v1/prediction/sleep_events/{}/{}'
k_uri = 'https://research-api-benjo.hello.is/v1/prediction/timeline/{}/{}'
k_magic_auth = '7.e0aa1ca0289449f5b3b3c257da9523ec'
num_days = 1
valid_keys = ['SLEEP','OUT_OF_BED','IN_BED','WAKE_UP']
def get_time_as_string(timestamp,offset):
    t = datetime.datetime.utcfromtimestamp(( offset + timestamp)/1000)
    return t.strftime('%Y-%m-%d %H:%M:%S')

start_date_string = sys.argv[1]
user_id = int(sys.argv[2])


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
            response = requests.get(url,headers = headers)
            if not response.ok:
                print 'fail with %d on %s ' % (response.status_code,datestring)
                continue
   
            data = response.json()
            
            if len(data) == 0:
                print 'no responses found on %s' % datestring

            responses.append(data)
         
       
        
    return responses

def print_results(data):
    if len(data) == 0:
        print 'empty timeline'
        return

    if len(data[0]) == 0:
        print 'empty timeline'
        return

    data = data[0][0]['segments']
    for item in data:

	event_type = item['event_type']
        if event_type in valid_keys:
	    timestr = get_time_as_string(item['timestamp'],item['offset_millis'])
	    print timestr,event_type
                
if __name__ == '__main__':
        
    resp = pull_date_for_user(user_id)
    #print resp
    print_results(resp)

