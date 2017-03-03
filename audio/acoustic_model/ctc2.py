from keras.preprocessing import sequence
from keras.models import Model
from keras.layers import TimeDistributed,Dense, Activation, Embedding,Input,LSTM,Lambda,Dropout,merge
import keras.callbacks

from keras import backend as K
from keras.optimizers import SGD,Adam,Adagrad
import hello_audio_feats
import sys
import numpy as np
import tensorflow as tf

nb_epochs = 1000
the_batch_size=128

'''
ctc_batch_cost(y_true, y_pred, input_length, label_length)

Benjo says:
y_true defines the graph of the model on which forwards/backwards is being computed (cost func)
y_pred is the model output

samples is the number of of input sets
time_steps is the the nubmer of time steps in the output
num_categories is the dimension of the output vector at each time step (I think)

example
y_true: tensor (samples, max_string_length) containing the truth labels
y_pred: tensor (samples, time_steps, num_categories) containing the prediction, or output of the softmax
input_length: tensor (samples,1) containing the sequence length for each batch item in y_pred
label_length: tensor (samples,1) containing the sequence length for each batch item in y_true




'''

def ctc_lambda_func(args):
    y_pred, labels, input_length, label_length,mask = args
    # the 2 is critical here since the first couple outputs of the RNN
    # tend to be garbage:
    #y_pred = y_pred[:, 2:, :]
    return K.ctc_batch_cost(labels,tf.multiply(y_pred,mask), input_length, label_length)

def ctc_lambda_decode(args):
    y_pred,input_length = args
    return K.ctc_decode(y_pred, input_length, greedy=True)#, beam_width=100, top_paths=1)


def data_to_vecs(data,label_sequences):
    max_time = 0
    max_symbols = 0
    #find maximum length of labels and features so we can get the embeddings right
    feat_size = 0
    for key in data:
        feat_size = data[key].shape[1]
        q = data[key].shape[0]
        
        if q > max_time:
            max_time = q

        p = len(label_sequences[key])

        if p > max_symbols:
            max_symbols = p


    #dimensions are (sample, time, vec)
    nsamples = len(data)
    x = np.zeros((nsamples,max_time,feat_size))
    labels = np.ones((nsamples,max_symbols),dtype='int64')*-1
    count = 0

    label_lengths = []
    input_lengths = []
    for key in data:
        xd = data[key]
        x[count,0:xd.shape[0],0:xd.shape[1]] = xd
        input_lengths.append(xd.shape[0])
        
        ld = np.array(label_sequences[key],dtype='int64')
        labels[count,0:ld.shape[0]] = ld
        label_lengths.append(ld.shape[0])

        count += 1

    input_lengths = np.array(input_lengths,dtype='int64')
    label_lengths = np.array(label_lengths,dtype='int64')
    
    return x,labels,input_lengths,label_lengths,max_symbols

    

def main():
    #get the data
    data,label_sequences,symbol_indices = hello_audio_feats.read_all_data('./data/')
    x,x_labels,x_in_lens,x_label_lens,max_symbols = data_to_vecs(data,label_sequences)
    x = x.astype('float32')
    input_shape = (x.shape[1],x.shape[2])
    num_phonemes = len(symbol_indices)

    #symbolic graph stuff#
    #the neural net

    #bidirectional
    input_data = Input(name='the_input', shape=input_shape, dtype='float32')
    lstm1_forward = LSTM(128,return_sequences=True,name='LSTM1_FORWARD',init='he_normal')(input_data)
    lstm1_backward = LSTM(128,return_sequences=True,name='LSTM1_BACKWARD',init='he_normal',go_backwards=True)(input_data)
    lstm1_merged = merge([lstm1_forward, lstm1_backward], mode='sum')
    dlstm1 = Dropout(0.2)(lstm1_merged)

    lstm2_forward = LSTM(128,return_sequences=True,name='LSTM2_FORWARD',init='he_normal')(dlstm1)
    lstm2_backward = LSTM(128,return_sequences=True,name='LSTM2_BACKWARD',init='he_normal',go_backwards=True)(dlstm1)
    lstm2_merged = merge([lstm2_forward, lstm2_backward], mode='sum')
    dlstm2 = Dropout(0.2)(lstm2_merged)
 
    dense = TimeDistributed(Dense(num_phonemes + 1,name='DENSE'))(dlstm2)
    y_pred = Activation('softmax', name='SOFTMAX')(dense)

    #stuff for the loss function
    output_shape = (x.shape[1],num_phonemes + 1)
    actual_mask = np.ones((x.shape[0],x.shape[1],num_phonemes + 1),dtype='float32')
    actual_mask[:,0:5,:] = 0.0
    for i in range(x_in_lens.shape[0]):
        actual_mask[i,x_in_lens[i]::] = 0.0
    
    input_length = Input(name='input_length', shape=[1], dtype='int64')
    label_length = Input(name='label_length', shape=[1], dtype='int64')
    mask = Input(name='mask',shape=output_shape,dtype='float32')
    labels = Input(name='labels', shape=[max_symbols], dtype='float32')
    loss_out = Lambda(ctc_lambda_func, output_shape=(1,), name='ctc')([y_pred, labels, input_length, label_length,mask])


    #the model with the net and the loss function
    model_loss = Model(input=[input_data, labels, input_length, label_length,mask], output=[loss_out])
    model_pred = Model(input=[input_data],output=[y_pred])
    model_pred.save('model_pred.h5')

    #optimizer
    sgd = SGD(lr=0.01, decay=1e-6, momentum=0.9, nesterov=True, clipnorm=5)
    #compile!
    model_loss.compile(loss={'ctc': lambda y_true, y_pred: y_pred}, optimizer=Adam())
    
    checkpoint_callback = keras.callbacks.ModelCheckpoint('weights.{epoch:04d}-{loss:.1f}--{val_loss:.1f}.h5', verbose=0, save_best_only=False, save_weights_only=False, mode='auto', period=1)

    #fit
    if len(sys.argv) >  2:
        model_loss.load_weights(sys.argv[2])

    if len(sys.argv) > 1 and sys.argv[1] == 'eval':
        y = model_pred.predict(x) * actual_mask

        y_tensor = K.variable(value=y)
        in_len_tensor = K.variable(value=x_in_lens)
        q = K.ctc_decode(y_tensor,in_len_tensor,greedy=True,beam_width=100, top_paths=1)[0][0]
        print K.eval(q)
    else:
	model_loss.fit([x,x_labels,x_in_lens,x_label_lens,actual_mask], [x_labels], batch_size=the_batch_size, nb_epoch=nb_epochs,callbacks = [checkpoint_callback],validation_split=0.2)

if __name__ == '__main__':
    main()

