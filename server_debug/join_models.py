#!/usr/bin/python
import online_hmm_pb2
import sys
import base64


def main(files):
    joined_models = online_hmm_pb2.AlphabetHmmUserModel()
    
    for fname in files:
        
        f = open(fname,'r')
        bindata = f.read()
        f.close()

        protobuf = online_hmm_pb2.AlphabetHmmUserModel()
        protobuf.ParseFromString(bindata)

        joined_models.models.extend(protobuf.models)


    f = open('joinedmodels.model','w')
    f.write(joined_models.SerializeToString())
    f.close()


if __name__ == '__main__':
    main(sys.argv[1:])
