#ifndef _TINYLSTM_NET_H_
#define _TINYLSTM_NET_H_

#include "tinylstm_types.h"
#include "tinylstm_tensor.h"

#define MAX_OUTPUT_SIZE (256)

#ifdef __cplusplus
extern "C" {
#endif

    
typedef struct {
    ConstLayer_t * layers;
    const uint32_t num_layers;
} ConstSequentialNetwork_t;
    
uint32_t get_network_output_size(const ConstSequentialNetwork_t * net);

Tensor_t * eval_net(const ConstSequentialNetwork_t * net,Tensor_t * input);
    


#ifdef __cplusplus
}
#endif



#endif //_TINYLSTM_NET_H_
