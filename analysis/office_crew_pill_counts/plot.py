#!/usr/bin/python
import datetime
import csv
from matplotlib.pyplot import *

def str2date(mystr):
    dt = datetime.datetime.strptime(mystr.strip(), '%Y-%m-%d')
    return dt


with open('results.csv') as f:
    reader = csv.reader(f)
    t = []
    c = []
    for line in reader:
        t.append(str2date(line[0]))
        c.append(int(line[1]))

    plot(t,c); grid('on')
    xlabel('Day (local_utc)')
    ylabel('num pill counts')
    title('num pill counts per day with office crew')
    show()
