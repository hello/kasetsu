#!/usr/bin/python
import numpy 
import numpy.random
import scipy.signal as signal
import struct
from pylab import *

N = 48000
Fs = 48000.0
Nwait = 48000
t = array(range(0, N)) / Fs
omega = 2 * numpy.pi * 20
b, a = signal.butter(2, 1.0/24)

#s = 2.0 * numpy.random.rand(N) - 1
s = numpy.sin(omega*t)


y = []
for i in range(10):
    y.extend(s)
    y.extend(numpy.zeros((Nwait,)))

#smooth out discontinuities
y2 = signal.filtfilt(b,a,y)

f = open('foo2.raw','w')

for i in xrange(len(y2)):
    f.write(struct.pack('h',int(y2[i] *32767)))
f.close()

