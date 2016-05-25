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
    
    uint32_t iout;
    uint32_t i;

    
    const uint32_t num_out_images = layer->weights->dims[0];
    const uint32_t num_images = layer->weights->dims[1];
    const uint32_t num_weights_rows = layer->weights->dims[2];
    const uint32_t num_weights_cols = layer->weights->dims[3];
    const uint32_t num_image_rows = in->dims[2];
    const uint32_t num_image_cols = in->dims[3];
    
    const Weight_t * weight_start = layer->weights->x;
    const uint32_t weight_filter_size = layer->weights->dims[1] * layer->weights->dims[2] * layer->weights->dims[3];
    
    const Weight_t * const image_start = in->x;
    const uint32_t image_size = in->dims[2] * in->dims[3];
    
    const Weight_t * bias = layer->biases->x;
    
    Weight_t * out_start = out->x;
    const uint32_t out_image_size = layer->output_dims[3] * layer->output_dims[2];
    
    assert(layer->weights->dims[1] == in->dims[1]);
    
    for (i = 0; i < TENSOR_DIM; i++) {
        assert(in->dims[i] == layer->input_dims[i]);
    }
    
    //make sure output tensor is ready for this
    for (i = 0; i < TENSOR_DIM; i++) {
        assert(out->dims[i] == layer->output_dims[i]);
    }

    // each of M filters is a 3D tensor (multiple "images") + bias weight
    // each filter has dimensions of 1 x N x P x Q, where P x Q is the filter image size
    // thus the filter, i.e. the weights will have dimensions of M x N x P x Q
    // the biases will have dimensions of M x 1 x 1 x 1
    //
    // there are N images, of size U x V
    // thus dims of the input are 1 x N x U x V
    //
    // and dims of the output are
    // 1 x M x (U - P + 1) x (V - Q + 1)
    //
    // so the idea is to build output images
    // from each filter
    
    for (iout = 0; iout < num_out_images; iout++) {
        
        tinylstm_convolve3d_direct(out_start, weight_start, image_start, *bias,num_weights_rows, num_weights_cols,num_image_rows , num_image_cols, num_images);
        
        //printf("\n\n");

        
        bias += 1;
        out_start += out_image_size;
        weight_start += weight_filter_size;
    }
    
}

ConstLayer_t tinylstm_create_conv_layer(const ConvLayer2D_t * static_def) {
    ConstLayer_t layer = {eval_conv2d_direct,get_conv2d_output_size,static_def};
    return layer;
}



