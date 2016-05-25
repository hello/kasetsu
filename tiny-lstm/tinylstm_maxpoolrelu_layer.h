#ifndef _TINYLSTM_MAXPOOLRELU_LAYER_H_
#define _TINYLSTM_MAXPOOLRELU_LAYER_H_


#include "tinylstm_tensor.h"

#ifdef __cplusplus
extern "C" {
#endif
    
typedef struct {
    const uint32_t * pool_dims;
    const uint32_t * output_dims;
    const uint32_t * input_dims;
} MaxPoolReluLayer_t;
    
ConstLayer_t tinylstm_create_conv_layer(const MaxPoolReluLayer_t * static_def);
    
    
#ifdef __cplusplus
}
#endif

#endif //_TINYLSTM_MAXPOOLRELU_LAYER_H_
