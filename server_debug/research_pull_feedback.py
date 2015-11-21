#!/usr/bin/python
import datetime
import calendar
import requests
import copy
import csv
import os

k_url = 'https://research-api-benjo.hello.is/v1/datascience/feedbackutc/{}'
k_magic_auth = os.environ['RESEARCH_TOKEN']
k_headers = {'Authorization' : 'Bearer %s' % k_magic_auth}

normiesA = [17627,30444,25012,44280,25691,41288,40829,40243,40038,30692,44469,20744,44324,38675,19106,42190,42528,35447,21709,19217,40818,40076,42502,43068,21075,30350,43142,42364,43554,41242,34722,33571,34113,31428,30909,26448,34370,24733,29595,25428,40969,42745,39662,24732,37590,38872,34320,43173,26669,40965,1768,1310,33873,35851,31745,16914,41892,38161,24335,36384,40256,30384,19219,41398,25094,41210,21899,1508,21468,35303,40558,37682,38680,42669,30221,42108,32469,33024,22747,39842,29761,30546,39811,41799,36130,35100,15070,23096,42688,20879,42353,42946,37897,40794,22199,44644,43897,30455,30085,34679]
normiesB = [36615,39952,40666,43478,32498,29772,30453,43054,38862,26275,23195,32962,35603,40259,38702,34029,30990,21562,41239,20809,15880,15249,1400,20409,18577,40941,29241,28824,39246,16017,38373,36723,18733,42846,38070,43430,29661,38867,41335,43223,43193,22176,25865,17714,1161,15030,25427,43357,21986,17687,17463,21150,33086,37468,17245,42680,20196,35574,25183,35193,37903,25976,40567,15159,32029,37359,34301,26885,39567,41149,15057,40832,42879,36304,22410,21201,29656,42359,39915,32434,18210,37372,40375,31453,43175,18057,32677,33494,23109,38825,38401,29651,42938,40013,39174,38914,22188,32022,27256,30302]
problemA = [23214,40541,27975,21638,42845,39151,32312,20946,25579,31962,19600,22373,40399,27882,41445,19905,15854,34392,42967,16214,22036,20604,42284,44339,30440,43648,38046,29507,25153,16435,28559,19865,30853,41150,32057,41245,18120,36546,19247,32305,42572,39993,19617,35833,41652,32539,38925,30177,23060,17790,41371,41425,39764,32686,17486,26632,43375,33818,28741,25947,38298,30906,26424,23317,31276,33311,22362,25243,16950,19256,34919,43541,32050,24396,40927,21077,22723,1817,42457,28822,20840,21385,21125,23566,22375,24639,31199,17239,1465,21911,42873,17095,28501,41695,33414]
problemB = [39167,42567,23615,29888,30124,15891,15116,37840,1086,34497,17195,41106,29982,38594,39172,25815,38749,42405,32238,31492,39078,18091,41473,42765,30055,18128,30060,41230,39765,30872,24117,30744,31520,34753,31671,1006,35467,24225,23068,27838,29802,38238,37693,25578,32071,16994,30606,30273,40736,34678,31648,26910,33453,16954,17984,27191,33199,17110,37830,24228,22984,40854,23624,38120,21469,33226,18858,16610,28762,20411,31140,23128,35300,41968,36052,30912,18383,1479,30358,42527,36662,41601,37335,23747,33461,41503,36591,19447,35144,43391,15073,39168,30394,41976,26276]

k_accounts_map = {'normiesA' : normiesA, 'normiesB' : normiesB, 'problemA' : problemA, 'problemB' : problemB}
#k_accounts_map = {'problemA' : problemA, 'problemB' : problemB}
#k_accounts_map = {'normiesA' : normiesA, 'normiesB' : normiesB}

k_min_date = '2015-11-16'
k_event_types = ['WAKE_UP','SLEEP']
k_fail_threshold = 30

def pull_data(account_id):
    responses = []
    
    params = {'min_date' : k_min_date}
    url = k_url.format(account_id)
    #print url
    response = requests.get(url,params=params,headers=k_headers)
        
    if not response.ok:
        print 'fail with %d on %s ' % (response.status_code,'foo')
        return []

    data = response.json()
        
    return data
       
def process_data(key,data,threshold,event_types):
    complaint_count = 0
    total_count = 0
    event_count = 0
    for item in data:
        if item['event_type'] not in event_types:
            continue

        delta = item['new_time_utc'] - item['old_time_utc']
        delta /= 60000

        if abs(delta) > threshold:
            complaint_count += 1
#            print key,delta,item['event_type'],item['account_id']

        total_count += 1

    return complaint_count,total_count
        
if __name__ == '__main__':
    
    for key in k_accounts_map:
        accounts_list = k_accounts_map[key]

        complaint_count = 0
        total_count = 0

        for account_id in accounts_list:
	    data = pull_data(account_id)
	    cc,tc = process_data(key,data,k_fail_threshold,k_event_types)

            total_count += tc
            complaint_count += cc
#            if tc > 0:
#                #print cc,tc
#	        total_count += 1
#                complaint_fraction  = cc / float(tc)
#	        complaint_count += complaint_fraction

        print key,complaint_count,total_count
 

