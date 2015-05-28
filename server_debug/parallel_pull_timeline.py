#!/usr/bin/python

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


POOL_SIZE = 8
#k_uri = 'http://ec2-52-1-32-223.compute-1.amazonaws.com/v1/prediction/sleep_events/{}/{}'
k_uri = 'https://research-api-benjo.hello.is/v1/prediction/sleep_events/{}/{}'
#k_uri = 'https://research.hello.is/v1/prediction/sleep_events/{}/{}'
k_magic_auth = '7.e0aa1ca0289449f5b3b3c257da9523ec'
k_users = [1, 1001, 1002, 1012, 1310, 1025, 1063, 1052]
k_algorithm = 'hmm'
k_params = {}

k_type_map = {'IN_BED' : 'PRED_IN_BED', 'SLEEP' : 'PRED_SLEEP', 'WAKE_UP' : 'PRED_WAKE_UP', 'OUT_OF_BED' : 'PRED_OUT_OF_BED'}
k_first_events = ['IN_BED','SLEEP']


def get_time_as_string(timestamp,offset):
    t = datetime.datetime.utcfromtimestamp(( offset + timestamp)/1000)
    return t.strftime('%Y-%m-%d %H:%M:%S')

def get_time_as_string_with_no_date(timestamp,offset):
    t = datetime.datetime.utcfromtimestamp(( offset + timestamp)/1000)
    return t.strftime('%H:%M')

def pull_date_for_user(label):
    userid = label['account_id']
    datestr = label['date']

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

def read_label_file(filename):
    items = []
    with open(filename,'rb') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            account_id = row['account_id']
            datestr = row['day_of_night']
            feedback = {}
            feedback['in_bed'] = row['in_bed']
            feedback['sleep'] = row['sleep']
            feedback['awake'] = row['awake']
            feedback['out_of_bed'] = row['out_of_bed']
            item = {}
            item['account_id'] = account_id
            item['date'] = datestr
            item['feedback'] = feedback

            items.append(item)
            
    return items

def print_results(item):
    
    for mydict in item:
            
        event_type = mydict['type']
        timestr = get_time_as_string(mydict['startTimestamp'],mydict['timezoneOffset'])
               
        print timestr,event_type
        
    print '\n'


def flatten_response(response):
    ret = {}
    found_items = []
    for item in response['data']:
        event_type = item['type']

        #if valid event
        if event_type in k_type_map.keys():

            #is in frist group? skip after finding the first
            if event_type in k_first_events:
                if event_type in found_items:
                    continue
                else:
                    found_items.append(event_type)
            
            timestr = get_time_as_string_with_no_date(item['startTimestamp'],item['timezoneOffset'])
            new_event_type = k_type_map[event_type]

            ret[new_event_type] = timestr

    return ret

def join_and_write_results(labels,responses,filename):
    mydict = {}

    #join responses and labels
    for item in labels:
        if item == None:
            continue
        
        key = str(item['account_id']) + '_' + item['date']
        if mydict.has_key(key):
            print 'duplicate of key %s, skipping.' % key
            continue
        
        mydict[key] = {}
        mydict[key]['label'] = item

    for item in responses:
        if item == None:
            continue
        
        key = str(item['account_id']) + '_' + item['date']

        if not mydict.has_key(key):
            print 'skipping response %s because it was not found in the labels' % key
            continue

        mydict[key]['response'] = item

    #flatten and write to csv file
    print 'starting writing to %s' % filename
    fieldnames = ['date', 'account_id','IN_BED','SLEEP','WAKE_UP','OUT_OF_BED','PRED_IN_BED','PRED_SLEEP','PRED_WAKE_UP','PRED_OUT_OF_BED']
    csvfile = open(filename,'wb')
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()
    for key in mydict:
        
        item = mydict[key]

        if not item.has_key('response'):
            continue

        
        label = item['label']
        response = item['response']
        feedback = label['feedback']
        
        flat_response = flatten_response(response)

 
        a = {'date' : label['date'],
             'account_id' : label['account_id'],
             'IN_BED' : feedback['in_bed'],
             'SLEEP' : feedback['sleep'],
             'WAKE_UP' : feedback['awake'],
             'OUT_OF_BED' : feedback['out_of_bed']}

        a.update(flat_response)

        writer.writerow(a)        

    csvfile.close()
    print 'done writing.'
        
                
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-i','--input', help = 'input label file',required=True)
    parser.add_argument('-o','--output', help = 'output resuults file',required=True)

    parser.add_argument('-a','--algorithm',default=k_algorithm)
    parser.add_argument('-p','--poolsize',default=POOL_SIZE,type=int)
    args = parser.parse_args()


    k_params['algorithm'] = args.algorithm
    
    labels = read_label_file(args.input)

    pool = Pool(args.poolsize)

    resp = pool.map(pull_date_for_user, labels)


    print 'retrieved %d items' % len(resp)

    join_and_write_results(labels,resp,args.output)

