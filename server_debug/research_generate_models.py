#!/usr/bin/python

import sys
import datetime
import requests
import numpy as np
import time
import json
import os

#@Path("/generate_models/{account_id}/{date_string}/{num_days}")
k_uri = 'https://research-api-benjo.hello.is/v1/prediction/generate_models/{}/{}/{}'
k_magic_auth = os.environ['RESEARCH_TOKEN']

def get_time_as_string(timestamp,offset):
    t = datetime.datetime.utcfromtimestamp(( offset + timestamp)/1000)
    return t.strftime('%Y-%m-%d %H:%M:%S')

start_date_string = sys.argv[1]
user_id = int(sys.argv[2])
num_days = int(sys.argv[3])
k_params = {}

def pull_date_for_user(userid):
    
    if userid is None:
        return None

    headers = {'Authorization' : 'Bearer %s' % k_magic_auth}
    mydate = datetime.datetime.strptime(start_date_string, '%Y-%m-%d')    
    datestring = mydate.strftime("%Y-%m-%d")
        
    url = k_uri.format(userid,datestring,num_days)

    response = requests.get(url,params=k_params,headers = headers)
    
    if not response.ok:
        print 'fail with %d on %s ' % (response.status_code,datestring)
        return None
    
    data = response.json()

    if isinstance(data,dict) and data.has_key('code') and int(data['code']) == 204:
        print data['message']
        return None                  

    print data.keys()


    if data['num_models_generated'] < 8:
        print 'not saving model -- not enough individual models in it'
        return data
    
    f = open(str(userid) + '.base64','w')
    f.write(data['model_protobuf'])
    f.close()
    
    return data
         
       
        


                
if __name__ == '__main__':
 
    resp = pull_date_for_user(user_id)

