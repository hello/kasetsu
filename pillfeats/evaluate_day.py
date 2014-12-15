#!/usr/bin/python
import sys

import extract_pill_data
import pillcsv
from pylab import *
from numpy import *

import segment_pill_data
if __name__ == '__main__':
    auth = sys.argv[1]
    date = sys.argv[2]
    data = extract_pill_data.get_info_for_day_from_server(auth, date)
    
    #{"account_id": 773, "timestamp": 1416025200000, 
    #"timezone_offset": -28800000, "value": 10224, "tracker_id": 738, "id": 550748}
    
    timelist = []
    valuelist = []
    for item in data:
        if item['value'] > 0:
            timelist.append(item['timestamp']/1000.0)
            valuelist.append(item['value'])
        
    
    datadict = {'day1' : [timelist, valuelist]}
    pillcsv.sort_pill_data(datadict)
    
    plot(array(timelist)/3600, valuelist,'.-')
    show()
    
    segs = segment_pill_data.process(datadict)
