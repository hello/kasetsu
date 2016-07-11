#!/usr/bin/python
import sys
from scipy.io import wavfile
import numpy as np
from matplotlib.pyplot import *


def load_data(filename):
    rate,data = wavfile.read(filename)

    if len(data.shape) > 1:
        data = data[:,0]

    if rate != 16000:
        print 'file %s is not 16khz' % (filename)
        sys.exit(0)

    data = data / 32768.

    return data

def conv_data(data,ref):

    N = data.shape[0] / ref.shape[0]

    if N < 3:
        print('data is not long enough')
        sys.exit(0)

    begin = int((N/2.0 - 0.5)*  ref.shape[0])
    end =   int((N/2.0 + 0.5) * ref.shape[0])

    print begin,end
    x = np.convolve(data,ref)
    x2 = x[begin:end]
    i = np.argmax(np.abs(x2))

    begin2 = i - 20
    end2 = begin2 + 1024
    xx = x2[begin2:end2]

    h = np.fft.fft(xx)
    f = np.linspace(0,8000,len(h)/2)
    a = 20*np.log10(np.abs(h[0:len(h)/2]))
    return f,a


if __name__ == '__main__':
    refdata = load_data('reference.wav')
    ref = refdata[::-1]

    datas = []

    fnames = []
    for i in range(1,len(sys.argv)):
        fname = sys.argv[i]
        data = load_data(fname)
        f,h = conv_data(data,ref)
        plot(f,h)
        fnames.append(fname)

    legend(fnames)
    grid('on')
    ylabel('power (dB)')
    xlabel('freq (Hz)')
    show()


