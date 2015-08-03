#!/usr/bin/python

import requests
import os
import sys
import csv
import argparse
import datetime
import json

k_out_filename = 'partnerfeedbacks.csv'

k_uri = 'https://research-api-benjo.hello.is/v1/prediction/alphabet/{}/{}'
k_magic_auth = os.environ['RESEARCH_TOKEN']

headers = {'Authorization' : 'Bearer %s' % k_magic_auth}

def pull_data(start_date_string,accountid,num_days):

    params = {}

    mydata = []


    mydate = datetime.datetime.strptime(start_date_string, '%Y-%m-%d')

    for iday in range(num_days):
        datestring = mydate.strftime("%Y-%m-%d")
        mydate += datetime.timedelta(days=1)
        url = k_uri.format(accountid,datestring)
        response = requests.get(url,params=params,headers = headers)
        
        if not response.ok:
            print 'fail with %d on %s ' % (response.status_code,datestring)
            continue


        data = response.json()
        
        if isinstance(data, dict) and data.has_key('code') and int(data['code']) == 204:
            print 'error on for %s on %s: %s' % (accountid,datestring,data['message'])
            continue


        print 'got data for user %s on day %s' % (accountid,datestring)

        mydata.append(data)

    return mydata


if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument('-o','--outfile')
    parser.add_argument('--date',required=True)
    parser.add_argument('-n','--numdays',default=1,type=int)
    parser.add_argument('--partnerfilter',default=False,action='store_true')
    parser.add_argument('-u','--user',help='user id number')
    args = parser.parse_args()

    mydata = pull_data(args.date,args.user,args.numdays)

    if args.outfile != None:
        print 'writing to %s' % args.outfile
        f = open(args.outfile,'w')
        json.dump(mydata,f)
        f.close()

    else:
        print mydata

