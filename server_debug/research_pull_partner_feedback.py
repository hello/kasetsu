#!/usr/bin/python

import requests
import os
import sys
import csv

k_out_filename = 'partnerfeedbacks.csv'

k_uri = 'https://research-api-benjo.hello.is/v1/datascience/partnerfeedback/{}'
k_magic_auth = os.environ['RESEARCH_TOKEN']
k_num_days = 3
k_params = {'num_days' : k_num_days}

headers = {'Authorization' : 'Bearer %s' % k_magic_auth}

def pull_data(datestring,event_type):
    url = k_uri.format(datestring)

    params = k_params
    params['event_type'] = event_type
    response = requests.get(url,params=k_params,headers = headers)

    if not response.ok:
        print 'fail with %d on %s ' % (response.status_code,datestring)
        return


    return response.json()


if __name__ == '__main__':

    if len(sys.argv) < 3:
        event_type = 'ALL_EVENTS'
    else:
        event_type = sys.argv[2]
        
    data = pull_data(sys.argv[1],event_type)

    if data == None:
        print ('no data found')
        sys.exit(0)

    f = open(k_out_filename,'w')


    writer = csv.DictWriter(f,fieldnames = ['account_id','query_date','event_type','new_time_utc','old_time_utc'])

    writer.writeheader()

    for row in data:
        writer.writerow(row)

    f.close()
    
    

                     
