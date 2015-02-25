#!/usr/bin/python
import sys
import numpy as np
from pylab import *
from numpy import genfromtxt
from scipy.signal import firwin
from scipy import signal
import os.path
import fnmatch
import re
import traceback


decimate_samples = 13

def filtfilt(B, A, x):
    firstpass = signal.lfilter(B, A, x)

    ## second pass to compensate phase delay
    secondpass = signal.lfilter(B, A, firstpass[::-1])[::-1]
    return secondpass

def get_list_of_files(globpatterns):
    includes = r'|'.join([fnmatch.translate(x) for x in globpatterns])
    myfiles = []
    for root, dirs, files in os.walk('.', followlinks=True):
        files.extend([os.path.join(root, f) for f in files])
        files = [f for f in files if re.match(includes, f)]
        myfiles.extend(files)

    return myfiles


if __name__ == '__main__':
    hpf = signal.firwin(21,0.1,pass_zero=False)
    lpf = np.ones((decimate_samples,))*1.0/decimate_samples
    
    files = get_list_of_files(['*.CSV', '*.csv'])
    y1 = []
    y2 = []
    y3 = []
    for file in files:
        print ('Processing %s' % (file))
        try:
            x = genfromtxt(file,delimiter=',',skip_header=10,skip_footer=2, usecols=(0,1,2,3));
            x = x.transpose()
            y1.extend(x[1, :])
            y2.extend(x[2, :])
            y3.extend(x[3, :])

        except Exception, e:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            lines = traceback.format_exception(exc_type, exc_value, exc_traceback)
            print(''.join('!! ' + line for line in lines))

    y1 = filtfilt(lpf, 1,y1)[0:-1:decimate_samples]
    y2 = filtfilt(lpf, 1,y2)[0:-1:decimate_samples]
    y3 = filtfilt(lpf, 1,y3)[0:-1:decimate_samples]

    np.savez(sys.argv[1], y1, y2, y3)

    plot(y1)
    plot(y2)
    plot(y3)
    show()


