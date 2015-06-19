#!/usr/bin/python

import sys
import datetime
import requests
import numpy as np
import time
import json
k_uri = 'http://127.0.0.1:9999/v1/timeline/'


def get_time_as_string(timestamp,offset):
    t = datetime.datetime.utcfromtimestamp(( offset + timestamp)/1000)
    return t.strftime('%Y-%m-%d %H:%M:%S')

'''
my_users = {'fm' : '3.120ca851b92d49cdae5e0e33eb02f171', 
           'mi' : '3.ea82af0895024eb2998150e1e9f83365', 
            'kik' : '4.9a1f7741f22a46959d7923a53f15776e', 
            'sp' : '4.4a4a066a56164203b0f2828096bcdc01', 
            'mar' : '3.9ffd3285bdc54adba5bfa74fc09bfdee', 
            'am' : '3.2260a267c7b54ad093d765c63f066dcc'
            }
'''

#my_users = {'sp' : '4.4a4a066a56164203b0f2828096bcdc01'}
my_users = {'fm' : '3.120ca851b92d49cdae5e0e33eb02f171' }
#my_users = {'kik' : '4.9a1f7741f22a46959d7923a53f15776e'}
#my_users={'am' : '3.2260a267c7b54ad093d765c63f066dcc'}

num_days = 5
start_date_string = '2015-02-15'
def pull_date(users_dict):
#    users_dict2 = {'fm' : users_dict['fm']}
    for user in users_dict:
        auth = users_dict[user]
        
        headers = {'Authorization' : 'Bearer %s' % auth}
    
        mydate = datetime.datetime.strptime(start_date_string, '%Y-%m-%d')
    
        for iday in range(num_days):
            datestring = mydate.strftime("%Y-%m-%d")
            url = k_uri + datestring
            mydate += datetime.timedelta(days=1)
            response = requests.get(url,params={},headers = headers)
    
    
    
            if response.ok:
                mylist = response.json()
                mydict = mylist[0]
                segs = mydict['segments']
                for seg in segs:
                    event_type = seg['event_type']
                    timestr = get_time_as_string(seg['timestamp'],seg['offset_millis'])
               
                    if event_type != 'SLEEPING' and len(event_type) > 1:
                        print user, timestr,event_type
    
                print datestring,'ok'
                #print('\a')
            else:
                print datestring,'fail'
   

if __name__ == '__main__':
    pull_date(my_users)
            

