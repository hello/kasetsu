#!/usr/bin/python

import sys
import datetime
import requests
import numpy as np
import time
import json
import sensecsv
import pillcsv
k_uri = 'http://127.0.0.1:9999/v1/timeline/'


#benjo
auth='9.8dc524e3dfb24b2d8838063eb6e89d02'
num_days = 2
start_date_string = '2015-01-30'
def pull_date():
    headers = {'Authorization' : 'Bearer %s' % auth}

    mydate = datetime.datetime.strptime(start_date_string, '%Y-%m-%d')

    for iday in range(num_days):
        datestring = mydate.strftime("%Y-%m-%d")
        url = k_uri + datestring
        mydate += datetime.timedelta(days=1)
        response = requests.get(url,params={},headers = headers)

        if response.ok:
            print 'ok'
        else:
            print 'fail'
   

if __name__ == '__main__':
    pull_date()
            

