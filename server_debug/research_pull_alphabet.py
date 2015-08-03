#!/usr/bin/python

import requests
import os
import sys
import csv
import argparse

k_out_filename = 'partnerfeedbacks.csv'

k_uri = 'https://research-api-benjo.hello.is/v1/prediction/alphabet/{}/{}'
k_magic_auth = os.environ['RESEARCH_TOKEN']

headers = {'Authorization' : 'Bearer %s' % k_magic_auth}

def pull_data(datestring,accountid):
    url = k_uri.format(accountid,datestring)

    params = {}
    response = requests.get(url,params=params,headers = headers)

    if not response.ok:
        print 'fail with %d on %s ' % (response.status_code,datestring)
        return


    print response.json()


if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument('--date',required=True)
    parser.add_argument('-n','--numdays',default=1,type=int)
    parser.add_argument('--partnerfilter',default=False,action='store_true')
    parser.add_argument('-u','--user',help='user id number')
    args = parser.parse_args()

    pull_data(args.date,args.user)
    
