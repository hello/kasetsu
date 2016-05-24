#ifndef _TINYLSTM_CONV_LAYER_
#define _TINYLSTM_CONV_LAYER_

#include "tinylstm_tensor.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef struct {
    const ConstTensor_t * weights;
    const ConstTensor_t * biases;
    const uint32_t output_dims[TENSOR_DIM];
    const uint32_t input_dims[TENSOR_DIM];

} ConvLayer2D_t;

ConstLayer_t tinylstm_create_conv_layer(const ConvLayer2D_t * static_def);

    
    
#ifdef __cplusplus
}
#endif

#endif //_TINYLSTM_CONV_LAYER_
