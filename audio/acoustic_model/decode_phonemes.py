import json
import hello_audio_feats
from keras.models import Model
from keras.models import load_model
import sys
from keras import backend as K
import numpy as np
from matplotlib.pyplot import *

istart = 0
aggro_mode = False

symbol_indices = json.load(open('symbols.json','r'))
symbol_lookup = {-1 : '' }
for key,value in symbol_indices.iteritems():
    symbol_lookup[value] = key
    


model = load_model('model_pred.h5')
model.load_weights(sys.argv[1])
xx = hello_audio_feats.get_feats_file(sys.argv[2])
input_shape = model.internal_input_shapes[0]
xx = xx[istart::,:]
if xx.shape[0] > input_shape[1]:
    xx = xx[0:input_shape[1],:]

x = np.zeros((1, input_shape[1],input_shape[2]))
x[0,0:xx.shape[0],0:xx.shape[1]] = xx
y = model.predict(x)

r1 = range(3)
y[0,r1,-1] = 1.0
y[0,r1,0:-1] = 0.0

if aggro_mode:
    themax = np.max(y[0,:,0:-1])
    print themax 
    y[0,:,0:-1] = y[0,:,0:-1] / themax

x_in_lens = np.array([x.shape[1]])
y_tensor = K.variable(value=y)
in_len_tensor = K.variable(value=x_in_lens)
q = K.ctc_decode(y_tensor,in_len_tensor,greedy=False,beam_width=50, top_paths=1)[0][0]

p = K.eval(q)[0]

print ' '.join([symbol_lookup[i] for i in p])

plot(y[0,:,:])
show()
