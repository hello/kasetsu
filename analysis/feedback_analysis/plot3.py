#!/usr/bin/python
import csv
from matplotlib.pyplot import *
import sys
import datetime
import numpy as np
import scipy.signal as signal
import json

def str2date(mystr):
    dt, _, us= mystr.partition(".")
    dt= datetime.datetime.strptime(dt, "%Y-%m-%dT%H:%M:%S")
    return dt

def main():
    with open(sys.argv[1],'r') as f:
        rates = json.load(f)

    ts = []
    vs = []
    
    for rate_dict in rates:
    
        my_list = []
        for k, v in rate_dict.iteritems():
            my_list.append((k,v))

        ordered_list = sorted(my_list, key=lambda tup: tup[0])

        t = []
        v = []
        for item in ordered_list:
            t.append(str2date(item[0]))
            v.append(item[1])

        v = filt_signal(v)

        ts.append(t)
        vs.append(v)

    lines = []
    for i in range(len(ts)):
        lines.append(plot(ts[i],vs[i]))

    grid('on');
    legend(['sleep complaint frac','wake complaint frac'])
    xlabel('Time')
    ylabel('Fraction')
    title('Smoothed Complaint Rate Vs. Time For All Users')
    setp(lines[0],linewidth=2)
    setp(lines[1],linewidth=2)
    ylim([0,0.10])
    show()
        
def filt_signal(x):
    N = 7.0
    B = np.ones(N) / N
    A = 1
    y = signal.filtfilt(B,A,x,padtype=None)
    return y
 

if __name__ == '__main__':
    main()
