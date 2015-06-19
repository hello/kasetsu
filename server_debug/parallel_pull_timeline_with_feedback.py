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
import os

POOL_SIZE = 8
#k_uri = 'http://ec2-52-1-32-223.compute-1.amazonaws.com/v1/prediction/sleep_events/{}/{}'
k_uri = 'https://research-api-benjo.hello.is/v1/prediction/sleep_events/{}/{}'
#k_uri = 'https://research.hello.is/v1/prediction/sleep_events/{}/{}'

k_magic_auth=os.environ['RESEARCH_TOKEN']

k_users = [18096, 19626, 17672, 20110, 15877, 16812, 16565, 17036, 15034, 19831, 19884, 17079, 19674, 17308, 20154, 17591, 17515, 17794, 15962, 19999, 19324, 17063, 20518, 17814, 18686, 19360, 19466, 20081, 16081, 18972, 19164, 17096, 17495, 19547, 18933, 19915, 15466, 15992, 17708, 20467, 19356, 18654, 16913, 18160, 19666, 18094, 18786, 17753, 15537, 19229, 15983, 17110, 17116, 17772, 20112, 19446, 19193, 15821, 17514, 15949, 18045, 17165, 17618, 19706, 16446, 19403, 1253, 17040, 16086, 17448, 17130, 18577, 20014, 20459, 1480, 17121, 20267, 1310, 17659, 19785, 16274, 18880, 18247, 20521, 18739, 18666, 16125, 17805, 17627, 15116, 19658, 19048, 18178, 15014, 1190, 19380, 17487, 17648, 16517, 15576, 17388, 19629, 19464, 17313, 16965, 15574, 16223, 19026, 20372, 19876, 16558, 20187, 16941, 17848, 18665, 17368, 18675, 1071, 17151, 16993, 17596, 16084, 18240, 1844, 18609, 18005, 1067, 17049, 15545, 17185, 18035, 17204, 16990, 18619, 17465, 19137, 15532, 19301, 17920, 18967, 17965, 17367, 20375, 19490, 17074, 20079, 17595, 18755, 18057, 19426, 18186, 17093, 20248, 17706, 18540, 20175, 18465, 18914, 18392, 18576, 18021, 17403, 18109, 18538, 17698, 17539, 17664, 19634, 17666, 17369, 19284, 16652, 17095, 20009, 16137, 18180, 18918, 19843, 19829, 17201, 16486, 17411, 15554, 1323, 19452, 18497, 20153, 17594, 17477, 17395, 17197, 18875, 19222, 20342, 19835, 19734, 20369, 16930, 17259, 18679, 17288, 17621, 16554, 17186, 17005, 1469, 17384, 17545, 18960, 16077, 20346, 18694, 15913, 18493, 20259, 18707, 16946, 15851, 18556, 18262, 19176, 17358, 16108, 17959, 18731, 16341, 16832, 18369, 19241, 19214, 18733, 18971, 19171, 15604, 19477, 16307, 16395, 16372, 15982, 19522, 19637, 20050, 18636, 17602, 19152, 18101, 17624, 17697, 20156, 20504, 18062, 15847, 17702, 19067, 15840, 16112, 18715, 16530, 18463, 16093, 18196, 16956, 17163, 17227, 18089, 1112, 15587, 16986, 17254, 17902, 16973, 17504, 16218, 17454, 19163, 15921, 1063, 15464, 19370, 17156, 18470, 17542, 16209, 17993, 18528, 16023, 17159, 19354, 18026, 17580, 18871, 18482, 15711, 17012, 16594, 15990, 19987, 19786, 15667, 17977, 18165, 16586, 17460, 19793, 19125, 17054, 17521, 18308, 20529, 18404, 20019, 16234, 18091, 20396, 17822, 19727, 16256, 19175, 18090, 20109, 20222, 19820, 1215, 18975, 17742, 16767, 18683, 20080, 1196, 19090, 17328, 1113, 20376, 18472, 17362, 17641, 15564, 16949, 19910, 16695, 16266, 17670, 15854, 18232, 20124, 17531, 17430, 19514, 17344, 15650, 15575, 17109, 18839, 18137, 19493, 16262, 1061, 19402, 19369, 18630, 16818, 16141, 20193, 19911, 18313, 19262, 17865, 17604, 18836, 20448, 19848, 1056, 1053, 20388, 1156, 17282, 18561, 18453, 20402, 16814, 15472, 19225, 20561, 18847, 19308, 16020, 17196, 17287, 19788, 20134, 19243, 19007, 19799, 19209, 17429, 16415, 15814, 17394, 17166, 18656, 1387, 20410, 17776, 16902, 19005, 15997, 17994, 1257, 19916, 16294, 17892, 19698, 17170, 18580, 17534, 17938, 16329, 17984, 19883, 17225, 17968, 20083, 20403, 20534, 18067, 1189, 19991, 17401, 16622, 18451, 17348, 16943, 18444, 18892, 20488, 17815, 17574, 19554, 19445, 17785, 16204, 16170, 15970, 15557, 17286, 19989, 16279, 18486, 20343, 18079, 15872, 20245, 1395, 1062, 15991, 20275, 19168, 19701, 19470, 18447, 17247, 19798, 20251, 17245, 17407, 19528, 17105, 20331, 19920, 1294, 16228, 20466, 17867, 1220, 19149, 17396, 19327, 19287, 20128, 19944, 18672, 18902, 17471, 20507, 19170, 17434, 18620, 17878, 19054, 1361, 18958, 17551, 19956, 17424, 16967, 17485, 18641, 20271, 20165, 18669, 19682, 16833, 20270, 18299, 17816, 19968, 18916, 17683]

k_algorithm = 'hmm'
k_params = {'partner_filter' : False}

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
        
def get_user_info(account_id,datestr,num_days):
    userinfo = []

    mydate = datetime.datetime.strptime(datestr, '%Y-%m-%d')

    for iday in range(num_days):
        datestring = mydate.strftime("%Y-%m-%d")
        mydate += datetime.timedelta(days=1)

        userinfo.append({'account_id' : account_id, 'date' : datestring})

    return userinfo
        
               
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-o','--output', help = 'output resuults file',required=True)
    parser.add_argument('--date',required=True)
    parser.add_argument('-n','--numdays',default=1,type=int)
    parser.add_argument('-a','--algorithm',default=k_algorithm)
    parser.add_argument('-p','--poolsize',default=POOL_SIZE,type=int)
    args = parser.parse_args()


    k_params['algorithm'] = args.algorithm

    userinfo = []
    for user in k_users:
        uinfo = get_user_info(user,args.date,args.numdays)
        userinfo.extend(uinfo)
        
    
    
    pool = Pool(args.poolsize)

    resp = pool.map(pull_date_for_user,userinfo)


    print 'retrieved %d items' % len(resp)

    join_and_write_results(resp,args.output)

