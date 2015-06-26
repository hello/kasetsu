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
#k_uri = 'https://research-api-benjo.hello.is/v1/prediction/sleep_events/{}/{}'
k_uri = 'https://research-api-benjo.hello.is/v1/prediction/sleep_events/{}/{}'
k_magic_auth=os.environ['RESEARCH_TOKEN']

k_users = [1, 1001, 1002, 1012, 1310, 1025, 1063, 1052]
k_users = [22531, 20110, 27520, 23137, 16812, 21203, 25871, 25643, 17036, 21125, 26009, 19674, 27230, 17591, 21409, 17000, 18629, 28361, 27611, 27954, 19915, 24562, 27776, 25342, 15992, 28192, 17508, 19666, 17209, 27997, 25983, 21561, 17116, 17842, 20325, 22817, 21330, 15626, 22813, 22139, 21543, 26952, 26479, 21780, 25649, 27535, 22905, 26882, 16911, 1253, 27352, 23988, 1060, 22808, 23453, 22945, 26618, 27196, 18577, 23157, 16929, 21032, 25707, 21828, 28163, 18301, 21374, 25722, 22168, 24552, 21911, 24952, 23910, 23062, 24335, 27301, 19380, 21335, 26917, 16517, 15576, 17388, 26813, 27221, 21936, 24829, 25428, 24463, 16223, 16941, 22647, 17688, 23256, 17354, 26099, 23325, 28318, 25700, 23805, 22034, 27438, 24603, 22305, 18534, 24255, 15779, 23370, 18240, 25435, 25046, 25120, 22132, 27049, 27190, 23429, 16519, 15545, 19131, 17912, 26422, 26118, 26600, 23712, 17965, 21569, 24211, 21090, 21190, 27127, 19490, 23628, 21860, 18186, 17093, 20028, 17706, 23053, 22334, 28208, 26184, 24110, 18392, 21003, 23028, 18538, 18109, 27882, 23469, 21205, 19298, 23732, 23514, 17664, 25864, 25170, 27727, 17593, 26918, 27631, 17440, 22540, 24495, 17095, 25224, 23319, 25094, 18245, 16178, 21257, 24825, 26448, 19304, 26098, 21274, 18910, 1188, 1003, 22327, 17687, 18497, 20350, 17065, 25661, 26123, 27459, 27097, 19222, 28176, 18159, 16950, 27604, 26279, 18679, 21812, 16644, 16554, 28125, 17005, 24583, 17032, 20686, 23077, 16403, 23866, 16077, 21735, 25935, 21289, 20219, 18493, 24672, 26225, 26502, 26203, 17911, 25971, 24959, 17651, 22318, 20966, 17959, 16154, 20589, 22226, 22699, 24435, 24494, 21486, 20050, 24314, 23585, 26640, 19212, 20892, 21328, 25836, 18315, 27616, 28409, 23107, 25429, 25617, 18463, 25359, 23116, 20996, 16093, 16956, 25425, 17163, 21902, 24694, 27389, 24368, 16992, 28154, 16986, 19099, 17216, 27439, 24451, 17504, 25843, 24108, 27962, 26107, 17542, 20587, 27204, 20994, 27819, 25854, 18528, 18783, 27320, 22879, 24520, 22306, 1194, 28052, 27298, 18120, 23083, 23088, 24532, 22748, 28275, 19469, 22049, 23940, 17977, 27639, 27311, 19793, 18559, 24723, 18308, 15959, 28435, 24525, 17234, 23017, 24406, 28351, 21088, 22462, 18091, 22117, 20019, 19068, 17822, 19727, 23055, 26611, 28127, 21110, 23747, 16834, 20222, 1215, 25568, 23557, 24401, 16767, 17742, 25728, 27208, 17328, 20376, 17641, 22871, 16624, 25006, 16949, 21168, 28165, 24398, 26595, 19842, 18224, 17256, 27213, 26137, 25382, 21558, 20816, 17174, 22058, 26032, 21372, 25966, 20833, 17344, 24871, 28354, 19387, 15611, 16118, 22757, 28389, 15575, 26849, 25235, 22485, 24759, 27531, 22511, 20845, 24758, 27781, 26663, 24304, 23590, 18982, 18210, 27046, 16818, 26641, 24155, 18015, 27074, 23277, 27941, 20448, 24716, 26001, 18527, 23974, 20483, 28445, 24533, 25407, 15472, 27318, 21319, 18431, 20134, 23274, 17450, 19209, 24029, 27753, 17714, 17240, 21299, 21378, 19208, 21165, 15997, 27233, 17994, 21226, 27800, 23096, 20404, 27560, 23672, 17717, 25306, 21638, 20216, 26421, 16479, 22310, 26417, 17488, 17984, 19883, 28048, 23479, 27496, 25273, 26869, 22166, 26795, 20998, 26274, 24732, 21446, 21918, 21570, 16622, 18451, 16943, 17195, 17124, 22177, 20003, 26718, 23644, 22413, 17058, 19445, 22811, 25098, 17785, 27056, 25162, 17547, 23267, 22115, 24262, 26906, 21706, 22455, 26270, 21277, 22541, 24866, 19701, 26522, 26013, 25228, 28166, 17245, 17105, 20131, 24249, 26874, 20379, 22729, 25057, 18768, 17867, 21261, 22077, 28132, 28343, 27034, 19115, 20507, 27010, 21962, 25406, 16268, 27641, 27996, 20667, 23247, 24544, 27565, 27374, 21997, 16967, 26548, 15594, 21986, 22440, 19353, 23043, 22750, 21113, 28255, 16220, 26605, 22774, 23743, 17289, 24445, 23643, 17933, 20805, 17308, 28319, 22155, 24736, 28228, 23251, 17063, 22014, 27943, 23065, 22102, 20897, 26788, 24969, 28017, 26133, 21579, 21258, 25505, 22761, 27152, 16933, 17193, 22609, 21633, 20467, 23133, 16913, 22354, 27198, 28122, 18786, 18094, 25201, 27730, 25894, 19229, 27804, 25056, 15983, 20782, 25537, 17538, 19193, 21881, 17514, 21562, 21007, 28144, 26897, 21683, 17618, 24971, 22086, 27927, 19516, 23219, 27802, 17944, 1422, 23400, 26553, 27295, 22987, 22859, 23812, 27870, 27437, 21494, 27442, 21231, 21978, 22429, 21825, 17121, 20990, 26121, 26729, 22075, 17652, 25891, 28021, 22771, 23589, 25985, 18739, 22437, 18666, 25613, 17627, 15116, 21628, 27764, 25272, 1190, 17038, 23913, 26276, 27885, 27120, 25978, 16587, 15574, 21312, 23341, 16965, 19500, 19026, 18508, 16558, 22448, 25779, 27883, 17848, 20955, 27414, 21779, 20992, 24054, 22686, 26827, 25879, 26424, 23725, 25038, 18609, 20819, 18005, 25153, 21798, 25822, 22886, 17204, 27970, 17465, 18619, 19137, 15532, 21809, 19301, 23374, 23226, 21187, 26405, 28099, 17367, 22815, 27527, 17074, 23222, 18057, 24164, 19006, 25908, 21497, 23377, 24946, 26024, 1216, 22537, 22884, 21759, 26272, 27864, 19625, 1072, 23034, 20791, 26351, 18696, 26675, 23297, 18555, 27966, 22714, 22733, 26450, 21597, 21017, 18180, 17491, 28401, 20057, 23240, 24429, 18405, 17197, 20000, 21060, 20342, 26558, 24225, 22353, 17746, 21719, 17583, 20373, 27149, 23533, 20987, 23701, 24217, 25775, 23645, 25580, 24034, 21874, 28088, 26980, 20141, 25976, 21709, 21150, 23977, 26486, 25444, 22239, 19197, 21886, 22133, 27636, 24519, 28434, 21906, 16860, 22161, 21249, 20323, 23760, 28229, 19214, 25022, 17342, 23621, 18733, 21847, 21557, 1610, 16307, 28487, 16395, 18636, 22183, 23100, 27395, 23693, 28432, 19152, 23050, 24978, 25582, 16934, 18062, 18464, 15847, 22640, 15840, 27420, 25691, 24222, 22791, 17558, 23364, 25731, 21745, 21158, 24248, 23880, 21786, 17254, 26097, 15488, 23013, 24094, 22864, 28271, 18470, 18362, 16209, 28124, 26412, 21889, 17159, 26103, 24357, 23976, 21469, 24610, 15711, 21171, 27912, 15990, 25555, 28278, 20957, 25301, 20666, 27843, 24885, 18697, 27835, 26311, 26936, 23236, 22472, 27766, 22003, 21961, 26114, 21367, 24009, 20171, 19340, 27322, 16127, 23622, 17940, 17020, 23680, 21356, 21265, 27055, 23063, 22560, 22111, 22375, 18975, 21802, 26030, 18098, 20080, 27731, 19090, 16214, 26643, 1172, 1113, 23600, 19206, 26234, 25889, 24414, 15564, 26792, 28388, 24114, 25811, 22481, 23604, 23694, 15489, 21653, 23868, 18439, 24754, 19219, 26012, 17430, 22784, 24050, 18049, 26797, 16262, 24238, 26105, 18630, 25839, 20193, 27193, 20535, 20954, 19262, 25680, 17765, 20829, 23093, 16066, 22206, 26824, 20293, 18847, 27904, 24594, 17196, 26746, 27495, 23234, 20976, 25401, 26683, 16520, 17166, 23186, 24167, 1257, 17258, 17892, 21855, 25570, 18726, 25426, 22858, 22742, 26129, 20729, 25111, 21643, 17534, 20043, 25024, 23023, 22646, 21736, 16329, 17225, 21701, 28058, 26752, 22314, 23964, 22007, 18067, 23124, 21686, 19529, 21129, 17296, 21749, 25640, 22642, 19462, 1436, 27418, 21967, 23721, 18892, 17713, 18738, 17815, 25830, 26292, 16204, 18583, 16170, 23293, 19989, 23415, 17286, 21952, 15487, 26504, 27517, 26149, 16871, 18079, 15872, 1395, 25609, 15991, 20275, 19285, 18190, 17721, 28115, 26761, 17374, 23873, 24870, 27492, 21290, 23787, 24833, 20698, 26527, 28112, 21075, 20776, 1294, 23392, 27504, 26249, 17396, 27281, 17123, 19287, 20128, 25491, 24793, 18672, 24437, 16948, 18634, 28199, 21949, 22799, 25865, 27682, 22776, 18620, 22973, 17878, 18614, 26447, 25053, 20802, 25685, 19290, 17424, 28156, 26049, 20835, 27964, 17615, 26889, 18669, 26253, 26785, 16362, 19968, 18916, 17556, 21866, 22001, 20305, 21380, 27752, 19884, 20879, 26026, 24811, 17794, 27197, 21023, 20518, 22984, 28315, 27227, 27564, 24819, 25055, 19255, 22716, 28363, 16160, 23401, 28211, 15465, 19624, 15466, 21831, 26774, 23563, 25522]
k_algorithm = 'hmm'
k_params = {'partner_filter' : False}

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

    for item in response['data']['alg_events']:

        if isinstance(item,list) and len(item) == 0:
            return ret
        
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
    fieldnames = ['date', 'account_id','LABEL_IN_BED','LABEL_SLEEP','LABEL_WAKE_UP','LABEL_OUT_OF_BED','PRED_IN_BED','PRED_SLEEP','PRED_WAKE_UP','PRED_OUT_OF_BED']
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
             'LABEL_IN_BED' : feedback['in_bed'],
             'LABEL_SLEEP' : feedback['sleep'],
             'LABEL_WAKE_UP' : feedback['awake'],
             'LABEL_OUT_OF_BED' : feedback['out_of_bed']}

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

