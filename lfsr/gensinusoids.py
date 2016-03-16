#!/usr/bin/python
import math
import numpy as np
from matplotlib.pyplot import *
import scipy.signal as sig
import sys


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
print "num cycles of carrier",num_cycles

t = np.array(range(0,int(num_cycles))) * Ts
thecos = (full_range * np.cos(wc*t)).astype(int)
thesin = (full_range * np.sin(wc*t)).astype(int)

write_vec(thecos,"cos_vec")
write_vec(thesin,"sin_vec")

f,h  =sig.welch(thecos)
plot(f,h); show()



