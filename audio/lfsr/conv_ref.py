#!/usr/bin/python
import sys
from scipy.io import wavfile
import numpy as np
from matplotlib.pyplot import *

PLOT_IMPULSE = True
target_rate = 16000

def load_data(filename):
    rate,data = wavfile.read(filename)

    if len(data.shape) > 1:
        data = data[:,0]

    if rate != target_rate:
        print 'file %s is not %dhz' % (filename,target_rate)
        sys.exit(0)

    data = data / 32768.

    return data

def conv_data(data,ref):

    N = data.shape[0] / ref.shape[0]
    print N
    if N < 3:
        print('data is not long enough')
        sys.exit(0)

    begin = int((N/2.0 - 0.5)*  ref.shape[0])
    end =   int((N/2.0 + 0.5) * ref.shape[0])

    print begin,end
    x = np.convolve(data,ref)
    x2 = x[begin:end]
    i = np.argmax(np.abs(x2))

    begin2 = i - 5
    end2 = begin2 + 1024
    xx = x2[begin2:end2]

    if PLOT_IMPULSE:
        dist = np.arange(xx.shape[0]).astype(float) / target_rate * 340.0 / 2.0
        xx2 = xx / np.max(np.abs(xx))
        plot(dist,xx2); xlabel('distance (m)'); title('normalized room response'); show()

    h = np.fft.fft(xx)
    f = np.linspace(0,target_rate,len(h)/2)
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


