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
import scipy.signal as sig

from sklearn.decomposition import FastICA

#k_uri = 'https://api.hello.is/v1/datascience/pill/'
#k_uri = 'http://localhost:9999/v1/datascience/pill/'
k_uri = 'http://ec2-52-1-32-223.compute-1.amazonaws.com/v1/datascience/pill/{}/{}'
k_auth = '7.e0aa1ca0289449f5b3b3c257da9523ec'


def get_url(email, datestr):
    return k_uri.format(email, datestr)
    
def get_info_for_day_from_server(email, datestring):
    
    headers = {'Authorization' : 'Bearer %s' % k_auth}
    url = get_url(email, datestr)
    print url
    response = requests.get(url,params={},headers = headers)
        
    if (response.ok):
        data = response.json()
        print ('got %d records of pill data' % (len(data)))
        return data
    else:
        return []

def get_unix_time_as_datetime(unix_time):
    return datetime.datetime.utcfromtimestamp(unix_time)
    
def get_pair_data(email1,email2,datestr):
    
    data1 = get_info_for_day_from_server(email1,datestr)
    data2 = get_info_for_day_from_server(email2,datestr)

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

    treal = np.linspace(t0, tf, N)  / 1000
    
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

    print pm.shape
    pm_filt = np.zeros(pm.shape)
    for i in xrange(pm.shape[1]):
        pm_filt[:, i] = sig.filtfilt(B, A, pm[:, i])
    
    
    
    x = concatenate((pm_filt[:, 0].reshape(pm_filt.shape[0], 1), pm_filt[:, 3].reshape(pm_filt.shape[0], 1)), axis=1)
    '''
    print x.shape
    plot(x[:, 0])
    plot(x[:, 1])
    show()
    '''
    
    ica = FastICA(n_components=2)
    y = ica.fit_transform(x)
    
    
    tdate = [datetime.datetime.utcfromtimestamp(t) for t in treal]
    
    cross_cov = np.matrix(y).transpose() * np.matrix(x)
    print cross_cov
    
    figure(1)
    ax = subplot(2, 1, 1)
    plot(tdate, y[:, 0])
    plot(tdate, y[:, 1])
    title('recovered')
    grid('on')
    
    subplot(2, 1, 2, sharex=ax)
    plot(tdate, x[:, 0])
    plot(tdate, x[:, 1])
    title('orig')
    grid('on')

    
    show()
    
if __name__ == '__main__':
    np.set_printoptions(precision=3, suppress=True, threshold=np.nan)
    datestr = '2015-02-19'
    
    email1 = 'fm@farhadmanjoo.com'
    email2 = 'aitchb@gmail.com'
    
    get_pair_data(email1, email2, datestr)
