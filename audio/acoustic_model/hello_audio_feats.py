
import glob
import csv
import os
import struct
import numpy as np
import sys

filetypestr = '*.lab'
data_file_ending = '.wav.bin'

def int16_unpack_array(bindata):
    N = len(bindata) / 2
    x = []
    for i in range(N):
        d = bindata[2*i:2*(i+1)]
        val = struct.unpack('h',d)
        x.append(val)

    return np.array(x)

def get_feats_file(fname):
    f = open(fname,'r')
    x = int16_unpack_array(f.read())
    x = x.reshape(x.shape[0] / 40,40).astype(float)
    f.close()
    return x


def get_key_from_filename(fname):
    fname = os.path.basename(fname)
    return fname.split('.')[0]

def get_symbols_from_file(fname):

    items = []
    with open(fname,'r') as csvfile:
        reader = csv.reader(csvfile,delimiter=' ')

        for line in reader:
            items.append(line[2])

    return items


def get_symbol_index_sequence(symbol_indices,relpath):
    files = glob.glob(relpath + filetypestr)
    sequences = {}
    for fname in files:
        symbols_sequence = get_symbols_from_file(fname)
        sequences[get_key_from_filename(fname)] = [symbol_indices[s] for s in symbols_sequence]

    return sequences
        

def get_all_unique_symbols(relpath):
    files = glob.glob(relpath + filetypestr)

    symbols = set([])
    for fname in files:
        symbols |=  set(get_symbols_from_file(fname))

    symbols = sorted(symbols)

    symbol_map = {}
    for i in range(len(symbols)):
        symbol_map[symbols[i]] = i
        
    return symbol_map


def read_all_data(relpath):
    symbol_indices = get_all_unique_symbols(relpath)
    label_sequences = get_symbol_index_sequence(symbol_indices,relpath)

    data = {}
    for key in label_sequences:
        x = get_feats_file(relpath + key + data_file_ending)
        data[key] = x

    return data,label_sequences,symbol_indices
    

    
def main():
    data,label_sequences,symbol_indices = read_all_data(sys.argv[1])
    print label_sequences
    print len(symbol_indices)
    
    
if __name__ == '__main__':
    main() 
