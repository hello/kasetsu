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


k_users = [1006, 1056, 1062, 1180, 1190, 1215, 1398, 15116, 15472, 15487, 15488, 15489, 15517, 15539, 15545, 15594, 15599, 15611, 15651, 15777, 15877, 15888, 15913, 15983, 15991, 16014, 16020, 16023, 16024, 16077, 16086, 1610, 16127, 16137, 16209, 16214, 16256, 16283, 16307, 16329, 16359, 16517, 16554, 16560, 16622, 16695, 16840, 16893, 16894, 16941, 16950, 16954, 17029, 17063, 17093, 17096, 17105, 17109, 17139, 17156, 17166, 17194, 17210, 17239, 17245, 17308, 17328, 17339, 17344, 17347, 17370, 17413, 17424, 17450, 17465, 17468, 17486, 17488, 17538, 17542, 17575, 17586, 17591, 17627, 17683, 17687, 17713, 17794, 17851, 17867, 17878, 17911, 17959, 17994, 18002, 18004, 18015, 18032, 18057, 18091, 18120, 18160, 18164, 18177, 18209, 18210, 18224, 18240, 18241, 18301, 18362, 18404, 18430, 18463, 1848, 18493, 18559, 18577, 18583, 18602, 18619, 18636, 18666, 18669, 18672, 18749, 18768, 18852, 18916, 18926, 18990, 19006, 19090, 1912, 19140, 19152, 19170, 19219, 19229, 19276, 19287, 19298, 19301, 19304, 19308, 19324, 19340, 19374, 19500, 19516, 19648, 19701, 19734, 19915, 19968, 20000, 20019, 20050, 20080, 20086, 20110, 20128, 20153, 20170, 20270, 20275, 20305, 20316, 20379, 20402, 20404, 20535, 20583, 20589, 20619, 20667, 20698, 20741, 20744, 20751, 20767, 20802, 20828, 20833, 20835, 20841, 20854, 20866, 20879, 20892, 20954, 20961, 20962, 20987, 20990, 20996, 21007, 21017, 21032, 21038, 21046, 21047, 21062, 21065, 21069, 21075, 21110, 21125, 21150, 21158, 21168, 21171, 21187, 21252, 21253, 21261, 21263, 21273, 21281, 21289, 21300, 21312, 21319, 21355, 21374, 21409, 21494, 21496, 21542, 21543, 21561, 21570, 21579, 21622, 21627, 21628, 21638, 21653, 21669, 21673, 21679, 21701, 21709, 21723, 21736, 21745, 21798, 21823, 21825, 21874, 21911, 21930, 21936, 21952, 21961, 21962, 21986, 21996, 22001, 22062, 22110, 22133, 22153, 22155, 22177, 22187, 22266, 22284, 22314, 22354, 22362, 22375, 22413, 22414, 22514, 22541, 22551, 22554, 22627, 22642, 22646, 22729, 22787, 22797, 22808, 22817, 22821, 22862, 22866, 22886, 22926, 22987, 23013, 23028, 23063, 23077, 23083, 23085, 23107, 23113, 23116, 23124, 23138, 23226, 23241, 23247, 23249, 23286, 23293, 23340, 23341, 23354, 23393, 23400, 23401, 23425, 23427, 23429, 23490, 23548, 23576, 23604, 23643, 23680, 23694, 23712, 23721, 23747, 23749, 23754, 23810, 23827, 23848, 23913, 23927, 24006, 24022, 24081, 24206, 24211, 24222, 24225, 24335, 24357, 24368, 24414, 24437, 24451, 24457, 24519, 24520, 24526, 24533, 24552, 24562, 24576, 24603, 24612, 24731, 24732, 24744, 24784, 24793, 24811, 24839, 24941, 24958, 24971, 24978, 25004, 25024, 25030, 25046, 25070, 25094, 25098, 25111, 25153, 25168, 25172, 25224, 25272, 25342, 25406, 25422, 25425, 25426, 25428, 25435, 25436, 25444, 25447, 25452, 25462, 25522, 25551, 25555, 25582, 25643, 25661, 25685, 25691, 25707, 25798, 25811, 25836, 25837, 25854, 25864, 25870, 25872, 25879, 25892, 25908, 25971, 25976, 25977, 25985, 26012, 26024, 26026, 26030, 26044, 26063, 26095, 26097, 26102, 26103, 26119, 26180, 26190, 26275, 26281, 26292, 26351, 26369, 26417, 26421, 26424, 26425, 26448, 26450, 26522, 26548, 26581, 26663, 26755, 26795, 26824, 26827, 26885, 26889, 26918, 26936, 27055, 27097, 27135, 27144, 27193, 27208, 27321, 27389, 27392, 27420, 27437, 27442, 27490, 27504, 27545, 27548, 27601, 27639, 27681, 27700, 27718, 27764, 27768, 27835, 27882, 27885, 27904, 28024, 28058, 28063, 28097, 28112, 28125, 28154, 28156, 28211, 28229, 28271, 28275, 28445, 28451, 28464, 28465, 28478, 28487, 28565, 28608, 28626, 28639, 28649, 28676, 28708, 28741, 28749, 28807, 28813, 28858, 28901, 28913, 29073, 29116, 29124, 29162, 29172, 29186, 29211, 29257, 29292, 29326, 29362, 29364, 29365, 29387, 29431, 29433, 29488, 29498, 29530, 29568, 29571, 29572, 29583, 29610, 29625, 29641, 29643, 29655, 29660, 29672, 29687, 29693, 29700, 29702, 29704, 29706, 29714, 29732, 29766, 29769, 29777, 29779, 29783, 29824, 29832, 29834, 29844, 29850, 29851, 29858, 29868, 29871, 29892, 29899, 29910, 29920, 29922, 29931, 29933, 29938, 29944, 29957, 29977, 29981, 29988, 30001, 30002, 30003, 30016, 30021, 30033, 30051, 30055, 30058, 30067, 30068, 30073, 30074, 30080, 30081, 30086, 30089, 30105, 30111, 30125, 30133, 30145, 30188, 30210, 30213, 30219, 30231, 30248, 30253, 30255, 30259, 30268, 30273, 30313, 30322, 30326, 30334, 30350, 30365, 30383, 30386, 30389, 30395, 30416, 30425, 30426, 30427, 30444, 30458, 30462, 30469, 30474, 30541, 30557, 30564, 30570, 30574, 30586, 30590, 30594, 30607, 30648, 30666, 30672, 30678, 30699, 30704, 30710, 30711, 30717, 30718, 30731, 30734, 30766, 30773, 30774, 30790, 30793, 30802, 30831, 30832, 30853, 30871, 30872, 30879, 30892, 30893, 30909, 30910, 30914, 30920, 30964, 30980, 30993, 31018, 31048, 31056, 31065, 31077, 31088, 31091, 31112, 31127, 31131, 31141, 31177, 31192, 31196, 31198, 31199, 31205, 31208, 31220, 31242, 31246, 31250, 31252, 31276, 31277, 31316, 31339, 31340, 31357, 31381, 31392, 31403, 31429, 31442, 31443, 31444, 31458, 31462, 31476, 31487, 31495, 31496, 31505, 31524, 31539, 31557, 31565, 31572, 31581, 31589, 31613, 31631, 31652, 31661, 31683, 31686, 31687, 31703, 31704, 31748, 31755, 31760, 31762, 31766, 31770, 31797, 31801, 31808, 31813, 31814, 31817, 31821, 31824, 31826, 31830, 31866, 31889, 31913, 31924, 31937, 31949, 31972, 31991, 32030, 32034, 32045, 32065, 32071, 32085, 32112, 32140, 32160, 32166, 32183, 32189, 32195, 32267, 32274, 32324, 32342, 32366, 32391, 32398, 32414, 32428, 32431, 32438, 32455, 32456, 32476, 32478, 32497, 32502, 32520, 32539, 32544, 32585, 32594, 32639, 32655, 32664, 32673, 32682, 32685, 32686, 32718, 32719, 32775, 32806, 32812, 32814, 32815, 32820, 32823, 32848, 32858, 32900, 32902, 32907, 32917, 32934, 32945, 32968, 32973, 32976, 33032, 33036, 33045, 33063, 33067, 33072, 33073, 33075, 33079, 33129, 33145, 33169, 33176, 33177, 33181, 33187, 33188, 33191, 33199, 33227, 33228, 33234, 33237, 33238, 33248, 33261, 33272, 33274, 33298, 33299, 33310, 33315, 33333, 33340, 33341, 33347, 33350, 33351, 33354, 33369, 33402, 33403, 33417, 33430, 33461, 33475, 33513, 33522, 33537, 33561, 33602, 33612, 33649, 33650, 33656, 33702, 33736, 33768, 33774, 33818, 33837, 33838, 33845, 33857, 33861, 33866, 33868, 33872, 33873, 33876, 33877, 33906, 33949, 33992, 33995, 34018, 34048, 34049, 34092, 34097, 34117, 34124, 34152, 34157, 34160, 34176, 34192, 34195, 34200, 34203, 34205, 34206, 34212, 34229, 34233, 34328, 34357, 34365, 34368, 34374, 34392, 34402, 34405, 34408, 34414, 34439, 34475, 34480, 34503, 34509, 34526, 34527, 34589, 34592, 34625, 34639, 34647, 34653, 34673, 34708, 34710, 34711, 34712, 34722, 34747, 34755, 34786, 34791, 34797, 34809, 34817, 34825, 34849, 34855, 34878, 34919, 34920, 34927, 34973, 35038, 35043, 35083, 35084, 35085, 35086, 35094, 35095, 35096, 35127, 35134, 35160, 35176, 35195, 35219, 35243, 35269, 35270, 35273, 35309, 35320, 35334, 35335, 35339, 35342, 35346, 35347, 35385, 35390, 35500, 35503, 35504, 35505, 35518, 35531, 35546, 35565, 35580, 35583, 35587, 35590, 35605, 35615, 35637, 35638, 35641, 35658, 35664, 35667, 35676, 35680, 35682, 35698, 35702, 35704, 35743, 35760, 35788, 35801, 35806, 35833, 35843, 35846, 35847, 35868, 35974, 35979, 35992, 35995, 36011, 36020, 36045, 36047, 36061, 36076, 36103, 36109, 36191, 36194, 36199, 36203, 36208, 36211, 36220, 36221, 36223, 36225, 36226, 36232, 36240, 36241, 36244, 36251, 36260, 36293, 36294, 36302, 36327, 36334, 36337, 36370, 36374, 36384, 36397, 36401, 36403, 36415, 36425, 36481, 36493, 36502, 36513, 36537, 36544, 36552, 36554, 36584, 36587, 36591, 36593, 36594, 36595, 36609, 36623, 36666, 36704, 36717, 36719, 36732, 36741, 36744, 36762, 36767, 36790, 36798, 36814, 36817, 36854, 36855, 36880, 36900, 36907, 36917, 36948, 36961, 36965, 36967, 36999, 37021, 37036, 37040, 37044, 37045, 37057]

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
    parser.add_argument('--partnerfilter',default=False,action='store_true')
    args = parser.parse_args()


    k_params['algorithm'] = args.algorithm
    k_params['partner_filter'] = args.partnerfilter

    userinfo = []
    for user in k_users:
        uinfo = get_user_info(user,args.date,args.numdays)
        userinfo.extend(uinfo)
        
    
    
    pool = Pool(args.poolsize)

    resp = pool.map(pull_date_for_user,userinfo)


    print 'retrieved %d items' % len(resp)

    join_and_write_results(resp,args.output)

