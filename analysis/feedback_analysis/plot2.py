#!/usr/bin/python

import csv
from matplotlib.pyplot import *
import sys
import datetime
import numpy as np
from collections import defaultdict

def str2date(mystr):
    dt = datetime.datetime.strptime(mystr.strip(), '%Y-%m-%d')
    return dt


def read_complaints_file(filename):
    cc = []
    t = []
    with open(filename,'r') as csvfile:
        reader = csv.reader(csvfile)
        for line in reader:
            if len(line) <= 1:
                continue
            t.append(str2date(line[0]))
            cc.append(int(line[1]))


    return t,cc


tc1,c1 = read_complaints_file('timelinecounts.txt')
tc2,c2 = read_complaints_file('wake_complaints.txt')
tc3,c3 = read_complaints_file('sleep_complaints.txt')

for i in range(len(c1)):
    c2[i] = c2[i] / float(c1[i])
    c3[i] = c3[i] / float(c1[i])
    
plot(tc1,c2,tc1,c3);
grid('on');
legend(['wake complaint frac','sleep complaint frac'])
xlabel('Time')
ylabel('Fraction')
title('Complate Rate vs Time')
show()
