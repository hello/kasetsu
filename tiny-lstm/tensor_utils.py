#!/usr/bin/python
import numpy as np
import copy
def print_fixed_point_tensor(name,weights):
    dims = weights.shape
    vec = (weights.flatten() * (2**7)).astype(int).tolist()
    vecstr = ['%d' % v for v in vec]
    myweights = 'const static Weight_t %s_weights[%d] = {%s};\n' % (name,len(vec),','.join(vecstr))
    mydims = 'const static uint32_t %s_dims[4] = {%d,%d,%d,%d};\n' % (name,dims[0],dims[1],dims[2],dims[3])
    mystruct = 'const static ConstTensor_t %s = {&%s_weights[0],&%s_dims[0]};\n' % (name,name,name)
    fname = '%s.c' % (name)
    print 'writing to %s' % fname
    with open('%s' % fname,'w') as f:
        f.write(myweights)
        f.write(mydims)
        f.write(mystruct)
        f.write('\n')

def print_conv_weights(name,weights):
    w = copy.deepcopy(weights)
    print w.shape
    for i in range(weights.shape[0]):
        for j in range(weights.shape[1]):
           w[i][j] = w[i][j][::-1,::-1]

    print_fixed_point_tensor(name,w) 
