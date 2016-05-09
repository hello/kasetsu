#!/usr/bin/python
import wave
import struct
import numpy as np
from matplotlib.pyplot import *

ref_wave_file = 'reference.wav'
input_wave_file = 'white.wav'

f_ref = wave.open(ref_wave_file,'r')
f_input = wave.open(input_wave_file,'r')

l1 = f_ref.getnframes();
l2 = f_input.getnframes()

ref = np.zeros((l1));
for i in range(l1):
    ref[i] = struct.unpack("<h",f_ref.readframes(1))[0];

x = np.zeros((l2));
for i in range(l2):
    x[i] = struct.unpack("<h",f_input.readframes(1))[0];

ref = ref / 32767.;
x = x / 32767.

y = np.convolve(x,ref[::-1])
plot(y)
show()
