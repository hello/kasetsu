#!/usr/bin/python
import math
import psycopg2
import os
import datetime
import time
from matplotlib.pyplot import *
import numpy as np
import pytz
import matplotlib.dates as mdates


account_id = 3431
k_pill_ids = ['B413B970EC030756','3B9B9B11A833C468']
start_time_utc = '2016-05-04 04:00:00'
#select * from pill_data_2016_05 where aid=3431;
ymax=3000

k_max_val = 10000

def zero_invalid_values(x):
    for i,v in enumerate(x):
        if abs(v) > k_max_val:
            if i > 0:
                x[i] = x[i-1]
            else:
                x[i] = x[i+1]

def get_pill_data(pill_id,conn):

    f = open('get_prox_data.str','r')
    query_str = f.read()
    f.close()

    query = query_str.format(pill_id,start_time_utc)
    cur = conn.cursor()

    cur.execute(query)

    ts = []
    prox4 = []
    prox = []

    for record in cur:
        time_with_zone = pytz.utc.localize(record[1], is_dst=None).astimezone(pytz.timezone('US/Pacific'))
        ts.append(time_with_zone)
        prox4.append(int(record[2]))
        prox.append(int(record[3]))


    zero_invalid_values(prox)
    zero_invalid_values(prox4)

    
    return ts,np.array(prox) - np.array(prox4),np.array(prox),np.array(prox4)
        

def main():
    conn = psycopg2.connect("dbname='sensors1' user='benjo' host='sensors2.cy7n0vzxfedi.us-east-1.redshift.amazonaws.com' port=5439 password='N33dzmoarcoffee'")

    data = []
    
    for pill_id in k_pill_ids:
        data.append(get_pill_data(pill_id,conn))

        

    conn.close()

    fig = figure(1)
    Nplots = len(data)
    for i,d in enumerate(data):
        t = d[0]
        t1 = t[0].replace(minute=0)
        tf = t[-1].replace(minute=0)
        if i == 0:
            ax = subplot(Nplots,1,i + 1)
        else:
            subplot(Nplots,1,i+ 1,sharex=ax)

#        ax.xaxis.set_major_formatter(mdates.DateFormatter('%a %H:%m'))
#        ax.xaxis.set_major_locator(mdates.HourLocator())
        plot(t,d[2])
        plot(t,d[3])
        xlim([t1,tf])
        #plot(t,d[3]-d[2],'.'o)

        fig.autofmt_xdate()
        title(k_pill_ids[i])
        grid('on')
    show()
if __name__=='__main__':
    main()


