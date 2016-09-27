#!/usr/bin/python
import sys
import datetime
import requests
import numpy as np
import time
import json
import signal
from multiprocessing import Pool
import threading
import csv
import argparse
import copy
import os

POOL_SIZE = 4
k_uri = 'https://research-api-benjo.hello.is/v1/prediction/sleep_events/{}/{}'
k_uri = 'http://127.0.0.1:9987/v1/prediction/sleep_events/{}/{}'

k_magic_auth=os.environ['RESEARCH_TOKEN']

#k_users = [1012,1310,1002]
#k_users = [1012]

k_algorithm = 'hmm'
k_params = {'partner_filter' : True}

k_type_map_prediction = {'IN_BED' : 'PRED_IN_BED', 'SLEEP' : 'PRED_SLEEP', 'WAKE_UP' : 'PRED_WAKE_UP', 'OUT_OF_BED' : 'PRED_OUT_OF_BED'}
k_type_map_feedback = {'IN_BED' : 'LABEL_IN_BED', 'SLEEP' : 'LABEL_SLEEP', 'WAKE_UP' : 'LABEL_WAKE_UP', 'OUT_OF_BED' : 'LABEL_OUT_OF_BED'}

k_first_events = ['IN_BED','SLEEP']


def get_time_as_string(timestamp,offset):
    t = datetime.datetime.utcfromtimestamp(( offset + timestamp)/1000)
    return t.strftime('%Y-%m-%d %H:%M:%S')

def get_time_as_string_with_no_date(timestamp,offset):
    t = datetime.datetime.utcfromtimestamp(( offset + timestamp)/1000)
    return t.strftime('%H:%M')

def pull_date_for_user(userinfo):
    userid = userinfo['account_id']
    datestr = userinfo['date']

    data = None    
    print "pulling for user " + str(userid)
    if userid is not None:
        
        headers = {'Authorization' : 'Bearer %s' % k_magic_auth}
        
        url = k_uri.format(userid,datestr)
        print url

        response = requests.get(url,params=k_params,headers = headers)
        if response.ok:

           
            data = response.json()

            if isinstance(data, dict) and data.has_key('code') and int(data['code']) == 204:
                print data['message']
                return None
            
            if len(data) == 0:
                print 'no responses found on date %s for user %s' % (datestr,str(userid))

        else:
            print 'fail with error %d on %s ' % (response.status_code,datestr)
            

    if data != None:
        datadict = {}
        datadict['data'] = data
        datadict['account_id'] = userid
        datadict['date'] = datestr
    else:
        datadict = None
                
    return datadict


def print_results(item):
    
    for mydict in item:
            
        event_type = mydict['type']
        timestr = get_time_as_string(mydict['startTimestamp'],mydict['timezoneOffset'])
               
        print timestr,event_type
        
    print '\n'

def process_events(events,is_feedback):
    ret = {}
    found_items = []

    for item in events:
        event_type = item['type']

        #if valid event
        if event_type in k_type_map_prediction.keys():

            #is in frist group? skip after finding the first
            if event_type in k_first_events:
                if event_type in found_items:
                    continue
                else:
                    found_items.append(event_type)
            
            timestr = get_time_as_string_with_no_date(item['startTimestamp'],item['timezoneOffset'])

            if is_feedback:
                new_event_type = k_type_map_feedback[event_type]
            else:
                new_event_type = k_type_map_prediction[event_type]

            ret[new_event_type] = timestr

    return ret

            
def flatten_response(response):
    ret = {}
    data = response['data']
    alg_events = data['alg_events']
    feedback_events = data['feedback_events']

    if len(feedback_events) == 0:
        return None

    ret.update(process_events(alg_events,False))
    ret.update(process_events(feedback_events,True))

    return ret

def join_and_write_results(responses,filename):
    mydict = {}

    for item in responses:
        if item == None:
            continue
        
        key = str(item['account_id']) + '_' + item['date']

        if not mydict.has_key(key):
            mydict[key] = {}
            
        mydict[key]['response'] = item
        mydict[key]['date'] = item['date']
        mydict[key]['account_id'] = item['account_id']

    #flatten and write to csv file
    print 'starting writing to %s' % filename
    fieldnames = ['date', 'account_id','LABEL_IN_BED','LABEL_SLEEP','LABEL_WAKE_UP','LABEL_OUT_OF_BED','PRED_IN_BED','PRED_SLEEP','PRED_WAKE_UP','PRED_OUT_OF_BED']
    csvfile = open(filename,'wb')
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()
    for key in mydict:
        
        item = mydict[key]
        
        flat_response = flatten_response(item['response'])

        if flat_response == None:
            continue

 
        a = {'date' : item['date'],
             'account_id' : item['account_id']}

        a.update(flat_response)

        writer.writerow(a)        

    csvfile.close()
    print 'done writing.'
                
               
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-o','--output', help = 'output resuults file',required=True)
    parser.add_argument('-n','--numdays',default=1,type=int)
    parser.add_argument('-a','--algorithm',default=k_algorithm)
    parser.add_argument('-p','--poolsize',default=POOL_SIZE,type=int)
    parser.add_argument('--partnerfilter',default=False,action='store_true')
    parser.add_argument('--forcelearning',default=False,action='store_true')
    parser.add_argument('-i','--input',required=True,help='input file, first column is accounts, second column is date')
    args = parser.parse_args()


    k_params['algorithm'] = args.algorithm
    k_params['partner_filter'] = args.partnerfilter
    k_params['force_learning'] = args.forcelearning

    userinfo = []

    with open(args.input,'r') as csvfile:
        reader = csv.reader(csvfile)
        for line in reader:
            item = {'account_id' : int(line[0]), 'date' : line[1].split(' ')[0]}
            userinfo.append(item)


    pool = Pool(args.poolsize)

    resp = pool.map(pull_date_for_user,userinfo)


    print 'retrieved %d items' % len(resp)

    join_and_write_results(resp,args.output)

