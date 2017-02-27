
import glob
import csv

filetypestr = '*.lab'

def get_symbols(fname):

    items = []
    with open(fname,'r') as csvfile:
        reader = csv.reader(csvfile,delimiter=' ')

        for line in reader:
            items.append(line[2])

    return items


def get_symbol_index_sequence(symbol_indices):
    files = glob.glob(filetypestr)
    sequences = {}
    for fname in files:
        symbols_sequence = get_symbols(fname)
        sequences[fname] = [symbol_indices[s] for s in symbols_sequence]

    return sequences
        

def get_all_unique_symbols():
    files = glob.glob(filetypestr)

    symbols = set([])
    for fname in files:
        symbols |=  set(get_symbols(fname))

    symbols = sorted(symbols)

    symbol_map = {}
    for i in range(len(symbols)):
        symbol_map[symbols[i]] = i
        
    return symbol_map


def main():
    symbol_indices = get_all_unique_symbols()

    sequences = get_symbol_index_sequence(symbol_indices)
    print sequences
    
if __name__ == '__main__':
    main() 
