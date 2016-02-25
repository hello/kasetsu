#!/usr/bin/python

import neuralnet_pb2
import argparse

def get_protobuf(paramsbindata,configdata,iddata):
    m = neuralnet_pb2.NeuralNetMessage()
    m.params = paramsbindata
    m.configuration = configdata
    m.id = iddata
    m.input_type = 0
    return m

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--params','-p',help='params file of binary data',required=True)
    parser.add_argument('--config','-c',help='config file with json data',required=True)
    parser.add_argument('--id',help='id you want to give this neural net',required=True)
    parser.add_argument('--output','-o',help='output binary file',required=True)
    args = parser.parse_args()

    f = open(args.params,'rb')
    bindata = f.read();
    f.close()
    f2 = open(args.config,'rb')
    config = f2.read();
    f2.close()

    p = get_protobuf(bindata,config,args.id)

    f = open(args.output,'wb')
    f.write(p.SerializeToString())
    f.close()
    
    

    
                        
                        
                        
    
    
