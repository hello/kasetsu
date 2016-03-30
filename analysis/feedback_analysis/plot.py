#!/usr/bin/python
import csv
from matplotlib.pyplot import *
import sys
import datetime
import numpy as np

def str2date(mystr):
    dt = datetime.datetime.strptime(mystr.strip(), '%Y-%m-%d %H:%M:%S')
    return dt

#by month
def get_month_key(dt):
    return str(dt.year) + '-' + str(dt.month)

def aggregate(dts,counts):
    agg = {}
    for i in range(len(dts)):
        key = get_month_key(dts[i])    
        if not agg.has_key(key):
            agg[key] = 0
        
        agg[key] += counts[i]

   
    agg_list = []
    for key in agg: 
        c = key.split('-')
        dt = datetime.datetime(year=int(c[0]),month=int(c[1]),day=1)
        agg_list.append((dt,agg[key]))

    agg_list.sort(key=lambda tup: tup[0])  
    return agg_list

def get_data_from_file(filename):
    x = []
    y = []
    
    with open(filename,'rb') as f:
        reader = csv.DictReader(f,delimiter=',')

        for line in reader:
            x.append(str2date(line['date_of_night']))
            y.append(float(line['count']))

    return (np.array(x),np.array(y))


def main():
    t1,x1 = get_data_from_file('SLEEP_count_over_30.csv')
    t2,x2 = get_data_from_file('WAKE_UP_count_over_30.csv')
    t3,x3 = get_data_from_file('active_accounts.csv')
    
    agg1 = aggregate(t1,x1)
    agg2 = aggregate(t2,x2)
    agg3 = aggregate(t3,x3)
    
    t = []
    xsleep = []
    xwake = []
    for i in range(len(agg1)):
        xwake.append(agg2[i][1] / agg3[i][1])
        xsleep.append(agg1[i][1] / agg3[i][1]) 
        t.append(agg1[i][0])

    figure(1)
    plot(t,xsleep, linewidth=2.0) 
    plot(t,xwake, linewidth=2.0); 
    xlabel('Time'); 
    ylabel('Fraction')
    title('Fraction of Active User Base Who Adjusted Events > 30 Minutes')
    grid('on')
    legend(['sleep event','wake event'])
      
    figure(2)
    plot(t3,x3,linewidth=2.0)
    xlabel('Time')
    title('Number of Active Users')
    ylabel('#  Users')
    grid('on')

    show()
if __name__ == '__main__':
    main()

