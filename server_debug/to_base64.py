#!/usr/bin/python

import sys
import base64

if len (sys.argv) < 3:
    print 'need to specify both input and output filenames'
    sys.exit(0)

f = open(sys.argv[1],'r')
bindata = f.read()
f.close()


f2 = open(sys.argv[2],'w')
f2.write(base64.b64encode(bindata))
f2.close()
