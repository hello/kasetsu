import neural_net_messages_pb2
import copy
import numpy as np
def numpy_mat_to_output_proto(mat):
    out = neural_net_messages_pb2.NeuralNetOutput()
    
    assert(len(mat.shape) == 2)

    M = mat.shape[0]
    N = mat.shape[1]

    for j in range(M):
        d = out.mat.add()
        d.vec.extend(mat[j,:].tolist())        

    return out

def input_to_numpy_mat(input_proto):
    M = len(input_proto.mat)

    if M == 0:
        return None

    mat = []
    for j in range(M):
        mat.append(copy.deepcopy(input_proto.mat[j].vec))

    return np.array(mat)
    
    


