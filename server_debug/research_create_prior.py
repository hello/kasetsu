#!/usr/bin/python

import datetime
import requests
import time
import json
import os
import csv


use_local = False
#k_users = [1012,32402]
k_users = [1012]
#k_users = [32402]

if use_local:
    k_magic_auth = '1.72a487bf3b2d4640b2eb5eea91e82b3e'
    k_url = 'http://localhost:9997/v1/prediction/create_prior/{}'
else:
    k_url = 'https://research-api-benjo.hello.is/v1/prediction/create_prior/{}'
    k_magic_auth=os.environ['RESEARCH_TOKEN']   


#1433116800000
#1420070400000
k_params = {'oldest_date_to_consider' : 1433116800000}

def get_time_as_string(timestamp,offset):
    t = datetime.datetime.utcfromtimestamp(( offset + timestamp)/1000)
    return t.strftime('%Y-%m-%d %H:%M:%S')




def pull_create_for_user(userid):
    headers = {'Authorization' : 'Bearer %s' % k_magic_auth}
    url = k_url.format(userid)

    response = requests.get(url,params=k_params,headers = headers)

    if response.ok:
        data = response.json()
        
        if isinstance(data, dict) and data.has_key('code') and int(data['code']) == 204:
            print data['message']
            return None


        if isinstance(data,list):
            print 'user %d got %d labels' % (int(userid),len(data))
            return data

    else:
        print 'fail with %d' % (response.status_code)

    return None
    

                   
if __name__ == '__main__':
    labels = []
    for iuser in range(len(k_users)):
        user = k_users[iuser]

        percentage_complete = iuser * 100 / len(k_users)

        print '%d%%' % percentage_complete,
        
        resp = pull_create_for_user(user)

        if resp != None:
            print len(resp)

