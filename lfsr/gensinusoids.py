#!/usr/bin/python
import math
import numpy as np
from matplotlib.pyplot import *
import scipy.signal as sig
import sys
import scipy.stats as stats

def write_vec(x,name):
    sys.stdout.write("\nconst int16_t %s[] = {" % name)
    for i in range(x.shape[0]):
        if i != 0:
            sys.stdout.write(",")
        sys.stdout.write("%d" % x[i])

    sys.stdout.write("};\n\n")
 

full_range = 32767
fs = 48000
Ts = 1.0 / fs

fc = 22000
Tc = 1.0 / fc
wc = fc * 2.0 * math.pi
num_cycles = Tc * 11.0 / (Ts)
num_cycles2 = 10000

print "num cycles of carrier",num_cycles

t = np.array(range(0,int(num_cycles))) * Ts
t2 = np.array(range(0,int(num_cycles2))) * Ts
#thecos = (full_range * np.cos(wc*t)).astype(int)
#write_vec(thecos,"cos_vec")

thesin = (full_range * np.sin(wc*t))
a = len(thesin)/2
x = (np.array(range(len(thesin)))- a) / (a/2.0)
y = stats.norm.pdf(x)
y = y / np.max(y)


q = np.array(y) * np.array(thesin)
plot(q); show()
write_vec(q.astype(int),"sin_vec")

f,h  =sig.welch(q)
#plot(f,10*np.log(h)); show()



