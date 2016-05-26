#ifndef _TINYLSTM_FULLYCONNECTED_LAYER_H_
#define _TINYLSTM_FULLYCONNECTED_LAYER_H_

#include "tinylstm_types.h"


typedef struct {
    const ConstTensor_t * weights;
    const ConstTensor_t * biases;
    const uint32_t * output_dims;
    const uint32_t * input_dims;
    SquashFunc_t squash;
} FullyConnectedLayer_t;

ConstLayer_t tinylstm_create_fullyconnected_layer(const FullyConnectedLayer_t * static_def);


#endif //_TINYLSTM_FULLYCONNECTED_LAYER_H_
