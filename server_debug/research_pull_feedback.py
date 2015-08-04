#!/usr/bin/python
import datetime
import calendar
import requests
import copy
import csv
import os

k_url = 'https://research-api-benjo.hello.is/v1/datascience/feedbackutc/{}'
k_magic_auth = os.environ['RESEARCH_TOKEN']
k_headers = {'Authorization' : 'Bearer %s' % k_magic_auth}


k_accounts_list = [1012]

#k_min_date = '2015-07-01'
#k_event_type = 'SLEEP'

k_min_date = None
k_event_type = None

def pull_data(account_id):
    responses = []
    
    params = {'min_date' : k_min_date}
    url = k_url.format(account_id)
    print url
    response = requests.get(url,params=params,headers=k_headers)
        
    if not response.ok:
        print 'fail with %d on %s ' % (response.status_code,'foo')
        return []

    data = response.json()
        
    return data
       
def process_data(data,threshold,event_type):
    complaint_count = 0
    
    for item in data:
        if event_type != None and event_type != item['event_type']:
            continue

        delta = item['new_time_utc'] - item['old_time_utc']
        delta /= 60000

        if delta > threshold:
            complaint_count += 1

    return complaint_count
        
if __name__ == '__main__':
    complaint_count = 0
    
    for account_id in k_accounts_list:
        data = pull_data(account_id)
        c = process_data(data,20,k_event_type)
        complaint_count +=  c

    print complaint_count
 

