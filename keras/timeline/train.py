#!/usr/bin/python
import keras.callbacks
from keras.models import Sequential,Graph
from keras.layers import LSTM
from keras.layers.core import TimeDistributedDense, Activation, Dropout
from keras.optimizers import SGD
from keras.optimizers import Adam
from keras.optimizers import Adagrad
import numpy as np
import raw_data
import sys
import os
import re


k_batch_size=32
k_num_epochs=40

optimizer = Adagrad()

def get_data():
    labels_files = ['labels_et12_2016-01-01_2016-03-10.csv000','labels_et14_2016-01-01_2016-03-10.csv000'] 
    files = os.listdir("./")
    csvfiles = [f for f in files if "csv" in f]
    raw_data_files = [f for f in csvfiles if "label" not in f]
    
    data = raw_data.load_data(sorted(raw_data_files),labels_files)
    return raw_data.get_inputs_from_data(data)
    

def train(fname):

    #setup callbacks
    filepath = fname + '_weights.{epoch:02d}-{val_loss:.2f}.h5'
    checkpoint_callback = keras.callbacks.ModelCheckpoint(filepath, monitor='val_loss', verbose=0, save_best_only=False, mode='auto')


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

    model.add_node(LSTM(256,return_sequences=True, go_backwards=False), name='forward1', input='input')
    model.add_node(LSTM(256,return_sequences=True, go_backwards=True), name='backward1',input='input')
    model.add_node(Dropout(0.5), name='dropout1', inputs=['forward1', 'backward1'])

    model.add_node(LSTM(128,return_sequences=True, go_backwards=False), name='forward2', input='dropout1')
    model.add_node(LSTM(128,return_sequences=True, go_backwards=True), name='backward2',input='dropout1')
    model.add_node(Dropout(0.5), name='dropout2', inputs=['forward2', 'backward2'])

    model.add_node(LSTM(64,return_sequences=True, go_backwards=False), name='forward3', input='dropout2')
    model.add_node(LSTM(64,return_sequences=True, go_backwards=True), name='backward3',input='dropout2')
    model.add_node(Dropout(0.5), name='dropout3', inputs=['forward3', 'backward3'])


    model.add_node(TimeDistributedDense(nb_classes,activation='softmax'), name='dense1', input='dropout3')
    model.add_output(name='output', input='dense1')
    print 'compiling...'
    model.compile(optimizer, {'output': 'categorical_crossentropy'})

    print 'saving config'
    with open(fname + '.json','w') as f:
        f.write(model.to_json())


    history = model.fit({'input':xx, 'output':ll},validation_split=0.1, batch_size=k_batch_size,nb_epoch=k_num_epochs,callbacks=[checkpoint_callback])

    model.save_weights(fname + '.h5',overwrite=True)

if __name__ == '__main__':
    fname = sys.argv[1]
    train(fname)
