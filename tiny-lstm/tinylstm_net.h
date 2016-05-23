#ifndef _TINYLSTM_NET_H_
#define _TINYLSTM_NET_H_

#include "tinylstm_types.h"
#include "tinylstm_tensor.h"

#define MAX_OUTPUT_SIZE (256)

#ifdef __cplusplus
extern "C" {
#endif

    /*
typedef enum {
  null = 0,
  conv_1d,
  conv_2d,
  maxpool,
  full
} EElementType_t;

    
// Weight matrix is multi-dimensional matrix (i.e. a tensor)
   //for all the elements,
   //for conv net, assuming square convolutions
 
 
typedef struct {
    EElementType_t type;
    const Weight_t * weights; //includes biases
    uint32_t num_inputs_per_unit;
    uint32_t num_outputs_per_unit;
    uint32_t num_units;
    SquashFunc_t squash_function;
    WeightLong_t * state; //optionally null
    //ActionCallback_t on_startup_function; //for readying memory from disk maybe?
    //ActionCallback_t on_shutdown_function;
} Element_t;
    */
    
/*
    FUNCTION POINTER DEFINITIONS
 */
typedef void (*LayerEval_t)(void * context,Tensor_t * out,const Tensor_t * in);
    
typedef uint32_t (*LayerSize_t)(void * context);
    
typedef void (*LayerDelete_t)(void * context);
    
/*
    CLASS DEFINITIONS
 */
typedef struct sLayer_t {
    LayerEval_t eval;
    LayerSize_t get_output_size_bytes;
    LayerDelete_t delete;
    void * context;
} Layer_t;
    
typedef struct {
    Layer_t * layers;
    const uint32_t num_layers;
} SequentialNetwork_t;
    
    

    
/*
   METHODS FOR SEQUENTIAL NETWORK
 */
uint32_t get_network_output_size(const SequentialNetwork_t * net);

Tensor_t * eval_net(const SequentialNetwork_t * net,Tensor_t * input);

#ifdef __cplusplus
}
#endif



#endif //_TINYLSTM_NET_H_
