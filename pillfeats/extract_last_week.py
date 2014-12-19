#!/usr/bin/python

import sys
import datetime
import requests
import sys
import numpy as np
import time
import json
import sensecsv
import pillcsv

k_uri = 'https://dev-api.hello.is/v1/datascience/pill/'
k_uri_light = 'https://dev-api.hello.is/v1/room/light/week'

#auth='1.968b8e23615447f9aef774553825a83f'
#auth = '1.54320790d7444b648cb56a832df41777'
auth = '1.631598871dbd4e4d8651d36392c1173f'
days_in_a_week = 7

def get_week_info():
    
    headers = {'Authorization' : 'Bearer %s' % auth}
    
    today = time.strftime("%Y-%m-%d")
    today = datetime.datetime.strptime(today, '%Y-%m-%d')
    mydate = today - datetime.timedelta(days=days_in_a_week)

    datelist = []
    
    pilldata = []
    for iday in range(days_in_a_week):
        datestring = mydate.strftime("%Y-%m-%d")
        response = requests.get(k_uri + datestring,params={},headers = headers)
        if response.ok:
            pilldata.extend(response.json())
        else:
            return None
            
        mydate += datetime.timedelta(days=1)

            
    
    response = requests.get(k_uri_light, params = {}, headers=headers)
    
    if not response.ok:
        return None
        
    lightdata = response.json()
        
        
    alldata = {}
    
    if len(pilldata) == 0:
        print 'no pill data found'
        return None
        
    account_id = str(pilldata[0]['account_id'])
    pill_id = str(pilldata[0]['tracker_id'])
    sense_id = '007'
    
    data = {}
    pill2 = [(p['value'], p['timestamp']/1000.0) for p in pilldata if p['value'] != -1]
    
    pillvalues = [p[0] for p in pill2]
    pilltimes = [p[1] for p in pill2]
    
    for i in range(len(pillvalues)):
        if (pillvalues[i] < 0):
            pillvalues[i] = 1
            
        
    
    data['pill'] = [pilltimes, pillvalues]
    
    
    sensetimes = [p['datetime']/1000.0 for p in lightdata]
    tempvalues = [0 for p in lightdata]
    humidityvalues = [0 for p in lightdata]
    lightvalues = [p['value'] for p in lightdata]

    sense = {account_id : {sense_id : [sensetimes, tempvalues, humidityvalues, lightvalues]}}
    sensecsv.sort_sense_data(sense)
    
    pill = {account_id : {pill_id : [pilltimes, pillvalues]}}
    pillcsv.sort_pill_data(pill)
    
    alldata = {}
    alldata['pill'] = pill
    alldata['sense'] = sense
    
    return alldata

