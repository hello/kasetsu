#!/usr/bin/python
import sys
import json
from numpy import *

q = 10


def print_array(a):
    if len(a.shape) == 1:
        N = a.shape[0]
        M = 1
        isvec = True
    else:
        N = a.shape[1]
        M = a.shape[0]
        isvec = False
    sys.stdout.write('{')
    for j in xrange(M):
        if j != 0:
            sys.stdout.write(',\n')

        sys.stdout.write('{')
       
        for i in xrange(N):
            if i != 0:
                sys.stdout.write(',')

            if isvec:
                val = a[i]
            else:
                val = a[j,i]

            sys.stdout.write('%d' % val)

        sys.stdout.write('}')

    sys.stdout.write('};\n\n')

def to_fix(a):
    return  (array(a) * 2**q).astype(int) 
   
f = open(sys.argv[1],'r')
hmm = json.load(f)
f.close()
A = to_fix(hmm['A'])
for i in xrange(A.shape[0]):
    for j in xrange(A.shape[1]):
        if A[i,j] <= 0:
            A[i,j] = 1

myvecs = to_fix(hmm['vecs'])
myvars = to_fix(hmm['vars'])

print_array(A)
print_array(myvecs)
print_array(myvars)
