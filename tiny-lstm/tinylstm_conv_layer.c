#include "tinylstm_conv_layer.h"
#include "tinylstm_memory.h"
#include "tinylstm_math.h"
#include <assert.h>

static void get_conv2d_output_size(const void * context,uint32_t * dims) {
    const ConvLayer2D_t * layer = (const ConvLayer2D_t *)context;
    
    uint32_t i;
    for (i = 0; i < TENSOR_DIM; i++) {
        dims[i] = layer->output_dims[i];
    }
    
}

static void eval_conv2d_direct(const void * context,Tensor_t * out,const Tensor_t * in) {
    const ConvLayer2D_t * layer = (ConvLayer2D_t *)context;
    
    uint32_t iweight,islice;
    const uint32_t * weight_dims = &layer->weights->dims[0];
    const uint32_t * input_dims = in->dims;
    const uint32_t * output_dims = &layer->output_dims[0];
    
    Weight_t * out_row = out->x;
    const Weight_t * in_row = in->x;
    const Weight_t * weight_row = layer->weights->x;
    uint32_t i;
    
    for (i = 0; i < TENSOR_DIM; i++) {
        assert(input_dims[i] == layer->input_dims[i]);
    }
    
    /*
    for (iweight = 0; iweight < weight_dims[0]; iweight++) {
        in_row = in->x;
        
        for (islice = 0; islice < input_dims[0]; islice++) {
            
            //convolve 2D
            tinylstm_convolve2d_direct(out_row, layer->weights->x, in_row, weight_dims[1], weight_dims[2], input_dims[1], input_dims[2]);
            
            
            //increment output slice
            out_row += output_dims[1]*output_dims[2];
            
            //increment input slice
            in_row += input_dims[1]*input_dims[2];
        }
        
        weight_row += weight_dims[1]*weight_dims[2];
    }
    */
}

ConstLayer_t tinylstm_create_conv_layer(const ConvLayer2D_t * static_def) {
    ConstLayer_t layer = {eval_conv2d_direct,get_conv2d_output_size,static_def};
    return layer;
}



