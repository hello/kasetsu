#!/usr/bin/python
from keras.models import Sequential,Graph
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
    
    data = raw_data.load_data(sorted(raw_data_files),labels_file)
    return raw_data.get_inputs_from_data(data)
    

def train():

    print 'getting data...'
    xx,ll = get_data();
    
 
    print xx.shape
    print ll.shape

    ndata,timesteps,data_dim = xx.shape
    ndata,timesteps,nb_classes = ll.shape
        
    # expected input data shape: (batch_size, timesteps, data_dim)
    '''
    model = Sequential()
    model.add(LSTM(32,return_sequences=True,input_shape=(int(timesteps),int(data_dim))))
    model.add(Dropout(0.2))
    model.add(LSTM(32,return_sequences=True))
    model.add(Dropout(0.2))
    model.add(LSTM(32,return_sequences=True))
    model.add(Dropout(0.2))
    model.add(TimeDistributedDense(nb_classes))
    model.add(Activation('softmax'))
    adam = Adam(lr=0.001, beta_1=0.9, beta_2=0.999, epsilon=1e-08)
    model.compile(loss='categorical_crossentropy', optimizer=adam)
    print 'fitting....'
    model.fit(xx, ll,
              batch_size=12, nb_epoch=50, show_accuracy=True,
              validation_data=(xx, ll))
    '''

    model = Graph()
    model.add_input(name='input', input_shape=(int(timesteps),int(data_dim)))

    model.add_node(LSTM(32,return_sequences=True, go_backwards=False), name='forward1', input='input')
    model.add_node(LSTM(32,return_sequences=True, go_backwards=True), name='backward1',input='input')
    model.add_node(Dropout(0.5), name='dropout1', inputs=['forward1', 'backward1'])

    model.add_node(LSTM(32,return_sequences=True, go_backwards=False), name='forward2', input='dropout1')
    model.add_node(LSTM(32,return_sequences=True, go_backwards=True), name='backward2',input='dropout1')
    model.add_node(Dropout(0.5), name='dropout2', inputs=['forward2', 'backward2'])

    model.add_node(TimeDistributedDense(nb_classes,activation='softmax'), name='dense1', input='dropout2')
    model.add_output(name='output', input='dense1')
    print 'compiling...'
    adam = Adam(lr=0.001, beta_1=0.9, beta_2=0.999, epsilon=1e-08)

    model.compile(adam, {'output': 'categorical_crossentropy'})
    history = model.fit({'input':xx, 'output':ll}, batch_size=12,nb_epoch=25)

   

    with open('my_config.json','w') as f:
        f.write(model.to_json())
    model.save_weights('my_weights.h5')

if __name__ == '__main__':
    train()
