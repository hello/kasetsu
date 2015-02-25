#!/usr/bin/python
import requests
import sys
import numpy as np
from pylab import *
from copy import *
import datetime
#uri = 'https://dev-api.hello.is/v1/datascience/pill/'
uri = 'http://localhost:9999/v1/datascience/pill/'
target_date_string = sys.argv[1]
auth='6.a2432d1a17024ec5afb8daad4c5b44dd'
#auth = '1.54320790d7444b648cb56a832df41777'
#auth = '1.631598871dbd4e4d8651d36392c1173f'
#auth = '1.968b8e23615447f9aef774553825a83f'


def get_unix_time_as_datetime(unix_time):
    return datetime.datetime.utcfromtimestamp(unix_time)


if __name__ == '__main__':
    headers = {'Authorization' : 'Bearer %s' % auth}
    response = requests.get(uri + target_date_string,params={},headers = headers)

    if (response.ok):
        data = response.json()
        print ('got %d records' % len(data))
        validdata = [d for d in data if d['value'] > 0]
        times = [x['timestamp'] for x in validdata]
        vals = [x['value'] for x in validdata]
        offsets = [x['timezone_offset'] for x in validdata]
    
        if len(times) == 0:
            print ('no valid data for this day')
            sys.exit(0)

        mytimes = []
        for i in range(len(times)):
            t = times[i]
            val = vals[i]
            offset = offsets[i]    
            mytimes.append(get_unix_time_as_datetime((t + offset)/1000))

        plot(mytimes,vals,'o')
        title(sys.argv[1])
        show()
