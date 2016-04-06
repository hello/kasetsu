#!/usr/bin/python
from keras.models import Sequential
from keras.layers import LSTM, Dense
import numpy as np
import raw_data
import sys
def get_data():
    labels_file = 'labels_sleep_2016-01-01_2016-03-02.csv000'
    raw_data_files = ['2016-01-04.csv000']

    return raw_data.load_data(raw_data_files,labels_file)

    

def train():

    data = get_data();
    d = data[0] #hope that this is a typical case
    
    data_dim = len(d[0][0])
    timesteps = len(d[0])
    nb_classes = len(d[1][0])

    print "T=%d,N=%d,L=%d" % (timesteps,data_dim,nb_classes)

    #concatenate all the classes
    xx = []
    ll = []
    for x,l in data:
        xx.append(x)
        ll.append(l)

    xx = np.array(xx)
    ll = np.array(ll)

        
    # expected input data shape: (batch_size, timesteps, data_dim)
    model = Sequential()
    model.add(LSTM(32, return_sequences=True,
                   input_shape=(timesteps, data_dim)))  # returns a sequence of vectors of dimension 32
    model.add(LSTM(32, return_sequences=True))  # returns a sequence of vectors of dimension 32
    model.add(LSTM(32))  # return a single vector of dimension 32
    model.add(Dense(nb_classes, activation='softmax'))

    model.compile(loss='categorical_crossentropy', optimizer='rmsprop')

 
    model.fit(xx, ll,
              batch_size=64, nb_epoch=5, show_accuracy=True,
              validation_data=(xx, ll))

if __name__ == '__main__':
    train()
