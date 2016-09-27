#!/usr/bin/python
import json
import sys


N = len(sys.argv)

if N <= 2:
    print 'last arg is output file, so you need to put something before that'
    sys.exit(0)

files = []
jarray = []

print 'output file is  %s' % (sys.argv[N-1])


for i in range(1,N - 1):
    print 'opening %s...' % sys.argv[i]
    f = open(sys.argv[i],'r')
    jdata = json.load(f)
    f.close()
    jarray.extend(jdata)

print 'saving to %s' % (sys.argv[N-1])
f = open(sys.argv[N-1],'w')
json.dump(jarray,f)
f.close()
