from scipy.io import wavfile
import sys
import numpy as np


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

def save_data(filename,data):
    data *= 32768
    data = data.astype('int16')
    wavfile.write(filename,target_rate,data)


if __name__ == '__main__':

    if len(sys.argv) < 3:
        print 'need input and output filenames'
        sys.exit(0)

    x1 = load_data(sys.argv[1])
    x2 = load_data(sys.argv[2])

    L = np.min((x1.shape[0],x2.shape[0]))
    x1 = x1[0:L]
    x2 = x2[0:L]

    dx = x2 - x1
    dxsq = dx ** 2

    x3 = x1 ** 2 + x2 ** 2
    errfrac = np.sum(dxsq) / np.sum(x3) / float(L) + 1e-14
    print errfrac
    errdb = 10 * np.log10(errfrac)
 
    print errdb

    
