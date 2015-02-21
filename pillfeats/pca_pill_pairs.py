#!/usr/bin/python

import sys
import datetime
import requests
import sys
import numpy as np
from pylab import *
from copy import *
import time
import json
from MyPca import MyPca
import scipy.signal as sig

k_uri = 'https://api.hello.is/v1/datascience/pill/'

my_users = {'fm' : '3.120ca851b92d49cdae5e0e33eb02f171', 
            'mi' : '3.ea82af0895024eb2998150e1e9f83365', 
            'ki' : '4.9a1f7741f22a46959d7923a53f15776e', 
            'sp' : '4.4a4a066a56164203b0f2828096bcdc01', 
            'mar' : '3.9ffd3285bdc54adba5bfa74fc09bfdee', 
            'am' : '3.2260a267c7b54ad093d765c63f066dcc', 
            'ab' : '3.a64f9383d16948498ef26ac7e46cc636', 
            'tp' : '3.4893f18df31a42fdbe4672fede166a73', 
            'mar2' : '3.7976dee8ee464a26861f77d942bd0b9f', 
            'am2' : '2.1d8b5016a7384d6784e1787480da5a38'
            }
            
user_partners = [['ki', 'sp'], 
                ['fm', 'ab'], 
                ['mar', 'mar2'], 
                ['mi', 'tp'], 
                ['am', 'am2']]


def get_info_for_day_from_server(auth, datestring):
    
    headers = {'Authorization' : 'Bearer %s' % auth}
    response = requests.get(k_uri + datestring,params={},headers = headers)
        
    if (response.ok):
        data = response.json()
        print ('got %d records of pill data' % (len(data)))
        return data
    else:
        return []

def get_unix_time_as_datetime(unix_time):
    return datetime.datetime.utcfromtimestamp(unix_time)
    
def get_pair_data(pairs, datestr):
    
    data1 = get_info_for_day_from_server(my_users[pairs[0]],datestr)
    data2 = get_info_for_day_from_server(my_users[pairs[1]],datestr)

    if len(data1) == 0 or len(data2) == 0:
        return None
        
    t0_1 = data1[0]['timestamp'] + data1[0]['timezone_offset']
    t0_2 = data2[0]['timestamp'] + data2[0]['timezone_offset']
    
    t0 = t0_2
    if t0_1 < t0_2:
        t0 = t0_1
        
    tf_1 = data1[-1]['timestamp'] + data1[0]['timezone_offset']
    tf_2 = data2[-1]['timestamp'] + data2[0]['timezone_offset']
    
    tf = tf_2
    if tf_1 > tf_2:
        tf = tf_1
        
        
    targetkeys = ['value','on_duration_seconds', 'kickoff_counts']
    N = (tf - t0) / 1000 / 60 + 1
    abstime = (np.array(range(0, N)) * 60 + t0/1000).tolist()
    abstime = np.array([get_unix_time_as_datetime(t) for t in abstime])
    t1 = [(item['timestamp'] + item['timezone_offset'] - t0) / 1000 / 60 for item in data1]
    t2 = [(item['timestamp'] + item['timezone_offset'] - t0) / 1000 / 60 for item in data2]
    m1 = [[item[targetkeys[0]], item[targetkeys[1]], item[targetkeys[2]]]  for item in data1]
    m2 = [[item[targetkeys[0]], item[targetkeys[1]], item[targetkeys[2]]]  for item in data2]

    pm1 = [[0, 0, 0] for i in xrange(N)]
    pm2 = [[0, 0, 0] for i in xrange(N)]

    for i in xrange(len(t1)):
        pm1[t1[i]] = m1[i]
        
        
    for i in xrange(len(t2)):
        pm2[t2[i]] = m2[i]
        
    pm = np.concatenate( (np.array(pm1), np.array(pm2)),  axis=1)
    
    #smear to accout for timing mis-match
    B = np.ones((2, ))
    A = np.ones((1, ))

    pm_filt = np.zeros(pm.shape)
    for i in xrange(pm.shape[1]):
        pm_filt[:, i] = sig.filtfilt(B, A, pm[:, i])
    
    
    
    pca = MyPca()
    pca.fit(pm_filt, 2)
    if np.sum(pca.transform_[:, 0]) < 0:
        pca.transform_ = -pca.transform_
        
    if np.sum(pca.transform_[0:3, 1] < 0):
        pca.transform_[:, 1] = -pca.transform_[:, 1]
        
    x2 = pca.transform(pm_filt)
    
    powersig = x2[:, 0]
    diffsig = x2[:, 1]
    alpha = 0.25
    
    idx1 = where(diffsig > alpha)
    ps1 = powersig[idx1]
    pt1 = abstime[idx1]
    
    idx2 = where(diffsig < -alpha)
    ps2 = powersig[idx2]
    pt2 = abstime[idx2]
    
    print pca.transform_

    ax = subplot(2, 1, 1)
    plot(pt1, ps1, 'b.', pt2, ps2, 'r.')
    grid('on')
    title('classified pair pill data for %s vs %s on %s' % (pairs[0], pairs[1], datestr))
    ylabel('normalized feature magnitude')
    legend(pairs)
    
    subplot(2, 1, 2, sharex=ax)
    plot(abstime, diffsig, '.-')
    grid('on')
    ylabel('decision signal')
    show()
    
    
    print len(data1), len(data2)

    
if __name__ == '__main__':
    np.set_printoptions(precision=3, suppress=True, threshold=np.nan)

    for i in range(len(user_partners)):
        get_pair_data(user_partners[i], sys.argv[1])
