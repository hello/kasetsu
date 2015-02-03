#!/usr/bin/python
import sys
import scipy.stats
from pylab import *

p = scipy.stats.poisson(float(sys.argv[1]))
p2 = scipy.stats.poisson(float(sys.argv[2]))

v = []
v2 = []
for x in xrange(15):
    v.append(p.pmf(x))
    v2.append(p2.pmf(x))

plot(v,'.-')
plot(v2,'.-')
show()
