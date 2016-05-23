#ifndef _TINYLSTM_CONV_LAYER_
#define _TINYLSTM_CONV_LAYER_

#include "tinylstm_tensor.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef struct {
    const Tensor_t * weights;
    const uint32_t input_dims[3];
    const uint32_t output_dims[3];
    
} ConvLayer2D_t;

Layer_t * create_conv_layer(ConvLayer2D_t * static_def);

    
    
#ifdef __cplusplus
}
#endif

#endif //_TINYLSTM_CONV_LAYER_
