#!/usr/bin/python
from keras.models import Sequential
from keras.layers import LSTM
from keras.layers.core import TimeDistributedDense, Activation, Dropout
from keras.optimizers import SGD
from keras.optimizers import Adam
import numpy as np
import raw_data
import sys
import os
import re

def get_data():
    labels_file = 'labels_sleep_2016-01-01_2016-03-02.csv000'
    files = os.listdir("./")
    csvfiles = [f for f in files if "csv" in f]
    raw_data_files = [f for f in csvfiles if "label" not in f]
    
    return raw_data.load_data(sorted(raw_data_files),labels_file)

    

def train():

    print 'getting data...'
    data = get_data();

    dt = []
    for d in data:
        dt.append(len(d[0]))

    timesteps = np.median(dt)
    data_dim = len(d[0][0])
    nb_classes = len(d[1][0])

    data2 = []
    for d in data:
        if len(d[0]) == timesteps:
            data2.append(d)

    data = data2
    data2 = []
    for d in data:
        if len(d[1]) > 0:
            data2.append(d)
    
    print "found %d user-days" % len(data2)
    print "T=%d,N=%d,L=%d" % (timesteps,data_dim,nb_classes)

    #concatenate all the classes
    xx = []
    ll = []
    for x,l in data2:
        xx.append(x)
        ll.append(l)

    xx = np.array(xx)
    ll = np.array(ll)

    print xx.shape
    print ll.shape
        
    # expected input data shape: (batch_size, timesteps, data_dim)
    model = Sequential()
    model.add(LSTM(32,return_sequences=True,input_shape=(int(timesteps),int(data_dim))))
    model.add(Dropout(0.2))
    model.add(LSTM(32,return_sequences=True))
    model.add(Dropout(0.2))
    model.add(LSTM(32,return_sequences=True))
    model.add(Dropout(0.2))
    model.add(TimeDistributedDense(nb_classes))
    model.add(Activation('softmax'))
    
    print 'compiling...'
    adam = Adam(lr=0.001, beta_1=0.9, beta_2=0.999, epsilon=1e-08)
    sgd = SGD(lr=0.1, decay=1e-6, momentum=0.9, nesterov=True)
    model.compile(loss='categorical_crossentropy', optimizer=adam)


    print 'fitting....'
    model.fit(xx, ll,
              batch_size=64, nb_epoch=50, show_accuracy=True,
              validation_data=(xx, ll))

    with open('my_config.json','w') as f:
        f.write(model.to_json())
    model.save_weights('my_weights.h5')

if __name__ == '__main__':
    train()
