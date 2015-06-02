#!/usr/bin/python
import requests
import sys
import datetime
k_url = 'http://ec2-52-1-32-223.compute-1.amazonaws.com/v1/datascience/feedback/{}'
k_magic_auth = '7.e0aa1ca0289449f5b3b3c257da9523ec'

def get_time_as_string(timestamp,offset):
    t = datetime.datetime.utcfromtimestamp(( offset + timestamp)/1000)
    return t.strftime('%Y-%m-%d')

def pull_data(email):
    headers = {'Authorization' : 'Bearer %s' % k_magic_auth}
    url = k_url.format(email)    
    response = requests.get(url,params=None,headers=headers)

    if response.ok:
        data = response.json()
        return data

    return None

def print_feedback(feedback):
    print ','.join(['date','event_type','original_time','new_time'])
    for item in feedback:
        time = get_time_as_string(item['dateOfNight'],0)
        
        print ','.join([time,item['eventType'],item['oldTimeOfEvent'],item['newTimeOfEvent']])
        
    
if __name__ == '__main__':
    feedback = pull_data(sys.argv[1])

    if feedback != None:
        print_feedback(feedback)
    
