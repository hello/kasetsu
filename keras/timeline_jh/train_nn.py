#!/usr/bin/python
import keras.callbacks
from keras.models import Sequential
from keras.layers.wrappers import TimeDistributed
from keras.layers import  TimeDistributedDense,Dense, Dropout, Embedding, LSTM, Input, Bidirectional 
from keras.optimizers import Adagrad
import numpy as np
import sys
import os
import re


def getData(nlabels):
    data = r"./dataset_fixed_light"
    data_alt ="../dataset_alt"
    labels = "../labels_%d" %nlabels
    xx = 0
    ll = 0
    ww = 0
    l = 0
    print os.getcwd()
    os.chdir(data)

    n_files = 5# len(os.listdir('./')) /3
    for i in range(n_files):
        if i + 1 == 1:
            y = np.load('y_'+str(i+1)+'.npz')['arr_0']

        else:
            y =np.concatenate((y,np.load('y_'+str(i+1)+'.npz')['arr_0']), axis = 0)

    n_files = 5# len(os.listdir('./')) /3
    for i in range(n_files):
        if i + 1 == 1:
            xx = np.load('XX_'+str(i+1)+'.npz')['arr_0']
                
        else: 
            xx =np.concatenate((xx,np.load('XX_'+str(i+1)+'.npz')['arr_0']), axis = 0)            
    os.chdir(labels)
    for i in range(n_files):
        if i + 1 == 1:
#            print 'loading: ' + str(i + 1)
            l = np.load('l_'+str(i+1)+'.npz')['arr_0']
            ll = np.load('ll_'+str(i+1)+'.npz')['arr_0']
            ww = np.load('ww_'+str(i+1)+'.npz')['arr_0']
        else:
#            print 'loading: ' + str(i + 1)
            l =np.concatenate((l,np.load('l_'+str(i+1)+'.npz')['arr_0']), axis = 0)
            ll =np.concatenate((ll,np.load('ll_'+str(i+1)+'.npz')['arr_0']), axis = 0)
            ww =np.concatenate((ww,np.load('ww_'+str(i+1)+'.npz')['arr_0']), axis = 0)
#    print "shuffling data"
    xx,ll,ww,y,l = zeroOutData(xx,ll,ww,y,l)
    
    all = np.c_[xx.reshape(len(xx),-1), ll.reshape(len(ll), -1), l.reshape(len(l),-1),y.reshape(len(y),-1),
                ww.reshape(len(ww),-1)]
    np.random.shuffle(all)
    xx=all[:,:xx.size//len(xx)].reshape(xx.shape)
    ll=all[:,xx.size//len(xx):xx.size//len(xx)+ll.size//len(ll)].reshape(ll.shape)
    l =all[:,xx.size//len(xx)+ll.size//len(ll):xx.size//len(xx)+ll.size//len(ll) + l.size//len(l)].reshape(l.shape)
    y =all[:,xx.size//len(xx)+ll.size//len(ll) + l.size//len(l):xx.size//len(xx)+ll.size//len(ll) + l.size//len(l)+y.size//len(y)].reshape(y.shape)
    ww=all[:,xx.size//len(xx)+ll.size//len(ll)+ l.size//len(l)+y.size//len(y):].reshape(ww.shape)
    print "XX shape:", xx.shape
    print "ll shape:", ll.shape
    print "l shape:", l.shape
    print "y shape:", y.shape
    return xx,ll,y, ww

def zeroOutData(xx,ll,ww,y,l):
    xx_alt1 = xx
    ll_alt1 = ll
    ww_alt1 = ww
    n_nights, timesteps, data_dim = xx.shape 
    n_nights, timesteps, nb_classes = ll.shape
    for i in range(n_nights):
        uncertainty = np.random.randint(20)
        wake = y[i,2]+ uncertainty
        if wake > 0 and wake < timesteps:
            xx_alt1[i, wake:,:] = np.zeros([timesteps-wake,data_dim])
            ll_alt1[i,wake:,:] = np.zeros([timesteps-wake,nb_classes])
            ww_alt1[i,wake:]= np.zeros([timesteps-wake])
    xx_alt2 = xx
    ll_alt2 = ll
    ww_alt2 = ww
    n_nights, timesteps, data_dim = xx.shape 
    for i in range(n_nights):
        uncertainty = np.random.randint(40)
        oob = y[i, 3]+ uncertainty
        if oob > 0 and oob < timesteps:
            xx_alt2[i, oob:,: ] = np.zeros([timesteps-oob,data_dim])
            ll_alt2[i,oob:,:] = np.zeros([timesteps-oob,nb_classes])
            ww_alt2[i,oob:]= np.zeros([timesteps-oob])                
    xx = np.concatenate((xx, xx_alt1, xx_alt2), axis = 0)
    ll = np.concatenate((ll, ll_alt1, ll_alt2), axis = 0)
    ww = np.concatenate((ww,ww_alt1,ww_alt2), axis = 0)
    y = np.concatenate((y,y,y), axis = 0)
    l = np.concatenate((l,l,l), axis = 0)
    return xx,ll,ww,y,l


def get_offset(l_single, timesteps):
    inbed_time = l_single[0]; out_of_bed_time = l_single[-1]
    window_space = 30
    floor = min(0, - inbed_time + window_space)
    ceiling = timesteps - (out_of_bed_time) + window_space

    offset = np.random.randint(floor, ceiling)
    return offset        

def batch_offset(xx,ll, ww,l):
    ndata, timesteps, data_dim = xx.shape
    ndata, timesteps, nb_classes = ll.shape
    padding = 120
    xx_batch = np.zeros([ndata, timesteps + 2 * padding,data_dim])
    ll_batch =np.zeros([ndata,timesteps+ 2 * padding, nb_classes]) 
    ww_batch = np.zeros([ndata, timesteps+ 2 * padding])
    xx_zeros = np.zeros([padding, data_dim])
    ll_zeros = np.zeros([padding,nb_classes])
    ww_zeros = np.zeros([padding])
    for i in range(ndata):
            offset = 0#get_offset(l[i], timesteps)
            ll_batch[i] = np.concatenate([ll_zeros, ll[i, offset:], ll[i, :offset],ll_zeros]).reshape([timesteps+2*padding, nb_classes])
            xx_batch[i] = np.concatenate([xx_zeros,xx[i, offset:], xx[i, :offset], xx_zeros]).reshape([timesteps+2*padding, data_dim])
            ww_batch[i] = np.concatenate([ww_zeros,ww[i, offset:], ww[i, :offset], ww_zeros]).reshape([timesteps+2*padding])
    return xx_batch, ll_batch, ww_batch

def train(fname, n_labels):

    k_batch_size = 128
    k_num_epochs = 1000
    val_split = 0.2
    dim1 = 128
    dim2 =64
    dim3 = 32
    dim4 = 32
    dropout_p = 0.2
    optimizer = Adagrad()

    #setup callbacks
    filepath = fname+'weights.{epoch:02d}-{val_loss:.2f}.h5'
    checkpoint_callback = keras.callbacks.ModelCheckpoint(filepath, monitor='val_loss', verbose=0, save_best_only=False, mode='auto')
    xx,ll,y,ww = getData(n_labels)
    print "Offsetting Time"
    xx, ll, ww = batch_offset(xx,ll,ww,y)
                                                                                
    os.chdir('../weights')
    print xx.shape
    print ll.shape
    print ww.shape

    ndata,timesteps,data_dim = xx.shape
    ndata,timesteps,nb_classes = ll.shape

    mode = 'gpu'
    model = Sequential()
    node1 = Bidirectional(LSTM(dim1, return_sequences = True, dropout_U=dropout_p, dropout_W= dropout_p, consume_less = mode), batch_input_shape = (ndata, timesteps, data_dim))
    node2 = Bidirectional(LSTM(dim2, return_sequences = True, dropout_U=dropout_p, dropout_W= dropout_p, consume_less = mode), batch_input_shape = (ndata, timesteps, data_dim))
    node3 = Bidirectional(LSTM(dim3, return_sequences = True, dropout_U=dropout_p, dropout_W= dropout_p, consume_less = mode), batch_input_shape = (ndata, timesteps, data_dim))
    node4 = Bidirectional(LSTM(dim4, return_sequences = True, dropout_U=dropout_p, dropout_W= dropout_p, consume_less = mode), batch_input_shape = (ndata, timesteps, data_dim))
    nodeEnd = TimeDistributed(Dense(nb_classes, activation = 'softmax'))

    model.add(node1)
    model.add(node2)
    model.add(node3)
#    model.add(node4)
    model.add(nodeEnd)    

    model.compile(optimizer = optimizer, loss='categorical_crossentropy', sample_weight_mode = 'temporal')
  
    
    print 'saving config'
    with open(fname + '.json','w') as f:
        f.write(model.to_json())

    history = model.fit(xx, ll,validation_split=val_split,batch_size=k_batch_size, nb_epoch=k_num_epochs, sample_weight = ww,callbacks=[checkpoint_callback])
    model.save_weights(fname + '.h5',overwrite=True) 
    

if __name__ == '__main__':
    fname = sys.argv[1]
    nlabels = int(sys.argv[2])
    train(fname, nlabels)    