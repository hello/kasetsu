from scipy.io import wavfile
import sys
import numpy as np
import scipy.signal as s

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
 
    f1, t1, S1 = s.spectrogram(x1)
    f2, t2, S2 = s.spectrogram(x2)
    
    dberr = 10*np.log10(S1) - 10*np.log10(S2)
    nbins = dberr.shape[0]
    
    errt = np.sum(dberr,axis=0) / nbins
    avgerr = np.sum(errt) / errt.shape[0]
    print avgerr
