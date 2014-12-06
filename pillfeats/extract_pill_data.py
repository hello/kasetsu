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

k_uri = 'https://dev-api.hello.is/v1/datascience/pill/'

def get_info_for_day_from_server(auth, datestring):
    
    headers = {'Authorization' : 'Bearer %s' % auth}
    response = requests.get(k_uri + datestring,params={},headers = headers)

    ibucket = 0
    mydict = {}
    energydict = {}
    if (response.ok):
        data = response.json()
        
        print ('got %d records' % len(data))
        
        return data

        '''
        validdata = [d for d in data if d['value'] > 0]
        times = [x['timestamp'] for x in validdata]
        vals = [x['value'] for x in validdata]

        if len(times) == 0:
            print ('no valid data for this day')
            sys.exit(0)

        t0 = times[0]
        #print (np.array(times) - t0) / 1000.0 / 3600.0
        #print vals
        for i in range(len(times)):
            t = times[i]
            val = vals[i]
            
            dt = t - t0
    
            #increment count in bucket
            if ibucket not in mydict.keys():
                mydict[ibucket] = 0
    
            mydict[ibucket] = mydict[ibucket] + 1
    
                
            if ibucket not in energydict.keys():
                energydict[ibucket] = 0
                
            energydict[ibucket] = energydict[ibucket] + val
                
            
            if dt > interval*ibucket:
                numperiods_to_advance = (dt - interval*ibucket) / interval
                ibucket = ibucket + numperiods_to_advance
            
        myhistogram = [0 for i in range(ibucket+1)]
        energies = [1 for i in range(ibucket+1)]
    
        for key in mydict.keys():
            myhistogram[key] = mydict[key]
            
        for key in energydict.keys():
            energies[key] = energydict[key]
            
            
    #    for i in range(len(energies)):
    #        energies[i] = np.log2(energies[i])
            
        smoothedenergies = copy(energies)
        for i in range(1, len(energies)):
            smoothedenergies[i] = energies[i-1] + energies[i]
            
        print myhistogram
        print energies
        
        plot (smoothedenergies)
        show()
        '''


def process():
    today = time.strftime("%Y-%m-%d")
    today = datetime.datetime.strptime(today, '%Y-%m-%d')

    days_in_past = int(sys.argv[2])
    auth = sys.argv[1]

    mydate = today - datetime.timedelta(days=days_in_past)
    datalist = []
    for iday in range(days_in_past):
        datestring = mydate.strftime("%Y-%m-%d")
        print datestring
        data = get_info_for_day_from_server(auth, datestring)

        if len(data) > 0:
            datalist.append(data)
        
        
        mydate += datetime.timedelta(days=1)

    return datalist
    
    
if __name__ == '__main__':
    datalist = process()
    
    f = open(sys.argv[3], 'w')
    json.dump(datalist, f)
    f.close()
    
