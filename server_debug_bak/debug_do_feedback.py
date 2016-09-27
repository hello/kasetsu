#!/usr/bin/python

import sys
import datetime
import requests
import numpy as np
import time
import json

k_url = 'http://127.0.0.1:9999/v1/feedback/sleep/'


def get_time_as_string(timestamp,offset):
    t = datetime.datetime.utcfromtimestamp(( offset + timestamp)/1000)
    return t.strftime('%Y-%m-%d %H:%M:%S')


my_users = {'fm' : '3.120ca851b92d49cdae5e0e33eb02f171', 
           'mi' : '3.ea82af0895024eb2998150e1e9f83365', 
            'kik' : '4.9a1f7741f22a46959d7923a53f15776e', 
            'sp' : '4.4a4a066a56164203b0f2828096bcdc01', 
            'mar' : '3.9ffd3285bdc54adba5bfa74fc09bfdee', 
            'am' : '3.2260a267c7b54ad093d765c63f066dcc'
            }


def do_feedback(auth):
    
    headers = {'content-type': 'application/json','Authorization' : 'Bearer %s' % auth}

     
    payload = {'date_of_night' : '2015-02-19', 
    'old_time_of_event' : '20:54' , 
    'new_time_of_event' : '21:05', 
    'event_type' : 'SLEEP'}
    
    data=json.dumps(payload)
    print data
    r = requests.post(k_url, headers=headers,data=data )

    print r.text

   

if __name__ == '__main__':
    do_feedback(my_users['sp'])
            

