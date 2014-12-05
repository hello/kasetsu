#!/usr/bin/python
import requests
import sys
import numpy as np
from pylab import *
from copy import *
uri = 'https://dev-api.hello.is/v1/datascience/pill/'
target_date_string = sys.argv[1]
auth = '1.54320790d7444b648cb56a832df41777'
#auth = '1.631598871dbd4e4d8651d36392c1173f'
#auth = '1.968b8e23615447f9aef774553825a83f'
headers = {'Authorization' : 'Bearer %s' % auth}
response = requests.get(uri + target_date_string,params={},headers = headers)

interval = 60*1000 * int(sys.argv[2])
ibucket = 0
mydict = {}
energydict = {}
if (response.ok):
    data = response.json()
    print ('got %d records' % len(data))
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
