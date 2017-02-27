#!/usr/bin/python
import sys
from matplotlib.pyplot import *
import numpy as np
import struct

def int16_unpack_array(bindata):
    N = len(bindata) / 2
    x = []
    for i in range(N):
        d = bindata[2*i:2*(i+1)]
        val = struct.unpack('h',d)        
        x.append(val)

    return np.array(x)

def get_file(fname):
    f = open(fname,'r')
    x = int16_unpack_array(f.read())
    print x.shape
    x = x.reshape(x.shape[0] / 40,40).astype(float)
    f.close()
    return x

def main():
    print sys.argv[1]
    x = get_file(sys.argv[1])
    X,Y = np.meshgrid(range(x.shape[1]),range(x.shape[0]))

    print np.max(x),np.min(x)
    pcolormesh(Y.transpose(),X.transpose(),x.transpose()) 
    xlabel('time (15ms frames)')
    ylabel('mel spectrogram bins')
    title(sys.argv[1].split("/")[-1])
    show()

if __name__ == '__main__':
    main()

