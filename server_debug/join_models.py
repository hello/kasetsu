#!/usr/bin/python
import online_hmm_pb2
import sys
import base64


def main(files):
    joined_models = online_hmm_pb2.AlphabetHmmUserModel()
    
    for fname in files:
        base = fname.split('.base64')[0].translate(None,'./')
        
        f = open(fname,'r')
        bindata = base64.b64decode(f.read())
        f.close()

        protobuf = online_hmm_pb2.AlphabetHmmUserModel()
        protobuf.ParseFromString(bindata)

        for model in protobuf.models:
            model.id = base + '-' + model.id
            print model.id

        joined_models.models.extend(protobuf.models)


    f = open('joinedmodels.model','w')
    f.write(joined_models.SerializeToString())
    f.close()


if __name__ == '__main__':
    main(sys.argv[1:])
