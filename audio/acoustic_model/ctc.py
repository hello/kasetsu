from keras.preprocessing import sequence
from keras.models import Model
from keras.layers import Dense, Activation, Embedding,Input,LSTM,Lambda
from keras import backend as K
from keras.optimizers import SGD
import hello_audio_feats
import sys

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
    y_pred, labels, input_length, label_length = args
    # the 2 is critical here since the first couple outputs of the RNN
    # tend to be garbage:
    y_pred = y_pred[:, 2:, :]
    return K.ctc_batch_cost(labels, y_pred, input_length, label_length)

def data_to_vecs(data,label_sequences):
    max_time = 0
    max_symbols = 0
    #find maximum length of labels and features so we can get the embeddings right
    for key in data:
        
        q = data[key].shape[0]
        
        if q > max_time:
            max_time = q

        p = len(label_sequences[key])

        if p > max_symbols:
            max_symbols = p


    print max_time,max_symbols

    

    

def main():
    data,label_sequences,symbol_indices = hello_audio_feats.read_all_data('./data/')

    data_to_vecs(data,label_sequences)
    
    num_phonemes = len(symbol_indices)

    sys.exit(0)
    
    symbol_indices_map = get_all_unique_symbols()
    sequences_map = get_symbol_index_sequence(symbol_indices_map)


    labels = Input(name='the_labels', shape=[img_gen.absolute_max_string_len], dtype='float32')



    #the neural net
    input_data = Input(name='the_input', shape=input_shape, dtype='float32')
    lstm1 = LSTM(32)(input_data,return_sequences=True,name='LSTM1')(input_data)
    lstm2 = LSTM(32,return_sequences=True,name='LSTM2')(lstm1)
    dense = Dense(num_phonemes,name='DENSE')(lstm2)
    y_pred = Activation('softmax', name='SOFTMAX')(dense)

    #stuff for the loss function
    input_length = Input(name='input_length', shape=[1], dtype='int64')
    label_length = Input(name='label_length', shape=[1], dtype='int64')
    labels = Input(name='LABELS', shape=[num_phonemes], dtype='float32')
    loss_out = Lambda(ctc_lambda_func, output_shape=(1,), name='ctc')([y_pred, labels, input_length, label_length])

    #the model with the net and the loss function
    model = Model(input=[input_data, labels, input_length, label_length], output=[loss_out])

    #optimizer
    sgd = SGD(lr=0.02, decay=1e-6, momentum=0.9, nesterov=True, clipnorm=5)

    #compile!
    model.compile(loss={'ctc': lambda y_true, y_pred: y_pred}, optimizer=sgd)

    #fit
    #model.fit(self, x, y, batch_size=32, nb_epoch=10)

if __name__ == '__main__':
    main()

