#!/usr/bin/python
import sys
from matplotlib.pyplot import *
import numpy as np

def get_file(fname):
    f = open(fname,'r')
    x = np.fromfile(f,dtype=np.int16)
    x = x.reshape(x.shape[0] / 40,40).astype(float)
    f.close()
    return x

def main():
    x = get_file(sys.argv[1])
    X,Y = np.meshgrid(range(x.shape[1]),range(x.shape[0]))

    print np.max(x),np.min(x)
    pcolormesh(Y.transpose(),X.transpose(),x.transpose()); xlabel('time (10ms frames)'); ylabel('mel bins'); show()

if __name__ == '__main__':
    main()

