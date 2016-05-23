#include "tinylstm_conv_layer.h"
#include "tinylstm_memory.h"
#include <assert.h>

static uint32_t get_conv2d_output_size(void * context) {
    const ConvLayer2D_t * layer = (ConvLayer2D_t *)context;
    return layer->output_dims[0]*layer->output_dims[1]*layer->output_dims[2] * sizeof(Weight_t);
}

static void eval_conv2d_direct(void * context,Tensor_t * out,const Tensor_t * in) {
    const ConvLayer2D_t * layer = (ConvLayer2D_t *)context;
    
    uint32_t iweight,islice;
    const uint32_t * weight_dims = &layer->weights->dims[0];
    const uint32_t * input_dims = in->dims;
    const uint32_t * output_dims = &layer->output_dims[0];
    
    Weight_t * out_row = out->x;
    const Weight_t * in_row = in->x;
    const Weight_t * weight_row = layer->weights->x;
    
    
    assert(input_dims[0] == layer->input_dims[0]);
    assert(input_dims[1] == layer->input_dims[1]);
    assert(input_dims[2] == layer->input_dims[2]);
    
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
}

static void delete_conv_layer(void * context) {
    FREE(context);
}

Layer_t * create_conv_layer(ConvLayer2D_t * static_def) {
    Layer_t * layer = MALLLOC(sizeof(Layer_t));
    
    layer->context = static_def;
    layer->eval = eval_conv2d_direct;
    layer->get_output_size_bytes = get_conv2d_output_size;
    layer->free = delete_conv_layer;
    
    return layer;
}

