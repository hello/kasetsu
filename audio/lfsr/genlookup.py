#!/usr/bin/python
import sys

for i in range(256):
    binstr = '{0:08b}'.format(i)
    num_ones = binstr.count('1')
    num_zeros = binstr.count('0')
    val = num_ones - num_zeros
    sys.stdout.write( "%d," % val)

sys.stdout.write('\n')
