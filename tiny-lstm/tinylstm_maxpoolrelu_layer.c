#include "tinylstm_maxpoolrelu_layer.h"
#include "tinylstm_memory.h"
#include <assert.h>


static void get_maxpoolrelu_output_size(const void * context,uint32_t * dims) {
    const MaxPoolReluLayer_t * layer = (const MaxPoolReluLayer_t *)context;
    
    uint32_t i;
    for (i = 0; i < TENSOR_DIM; i++) {
        dims[i] = layer->output_dims[i];
    }
    
}


/*   General idea is this: Given image of 4x4, a 2x4 max pool will produce a 2x1 image
 *   Another example 4x4 input, a 2x2 will produce a 2x2 result
 *   This is per-image
 *
 *   So input tensor will be 1 x N x P x Q
 *   output tensor will be 1 x N x L x M
 *
 *   where L = P / maxpool_cols, M = Q / max_pool_rows
 */
static void eval_maxpoolrelu(const void * context,Tensor_t * out,const Tensor_t * in) {
    const MaxPoolReluLayer_t * layer = context;
    
    const Weight_t * input_image_start = in->x;
    const uint32_t input_image_size = in->dims[3] * in->dims[2];
    
    Weight_t * output_image_start = out->x;
    const uint32_t output_image_size = out->dims[3] * out->dims[2];
    
    const uint32_t num_row_regions = in->dims[2] / layer->pool_dims[0];
    const uint32_t num_col_regions = in->dims[3] / layer->pool_dims[1];
    
    const uint32_t num_pool_rows = layer->pool_dims[0];
    const uint32_t num_pool_cols = layer->pool_dims[1];
    const uint32_t num_input_image_cols = in->dims[3];
    const uint32_t num_output_image_cols = out->dims[3];

    
    const uint32_t num_images = in->dims[1];
    uint32_t iimage,iregionrow,iregioncol;
    uint32_t j,i;
    
    
    
    assert (num_row_regions == out->dims[2]);
    assert (num_col_regions == out->dims[3]);
    
    assert( in->dims[3] %  layer->pool_dims[1] == 0);
    assert( in->dims[2] %  layer->pool_dims[0] == 0);

    for (iimage = 0; iimage < num_images; iimage++) {
        
        const Weight_t * input_image_row = input_image_start;
        Weight_t * output_image_row = output_image_start;

        for (iregionrow = 0; iregionrow < num_row_regions; iregionrow++) {
            for (iregioncol = 0; iregioncol < num_col_regions; iregioncol++) {
                
                Weight_t maxValue = -MAX_WEIGHT;
                
                for (j = 0; j < layer->pool_dims[0]; j++) {
                    for (i = 0; i < layer->pool_dims[1]; i++) {
                        maxValue = input_image_row[i] > maxValue ? input_image_row[i] : maxValue;
                    }
                    
                    input_image_row += num_input_image_cols;
                }
                
                output_image_row[iregioncol] = maxValue;
            
            }
            
            output_image_row += num_output_image_cols;
        }
        
        input_image_start += input_image_size;
        output_image_start += output_image_size;
    }
    
}

ConstLayer_t tinylstm_create_maxpoolrelu_layer(const MaxPoolReluLayer_t * static_def) {
    ConstLayer_t layer = {eval_maxpoolrelu,get_maxpoolrelu_output_size,static_def};
    return layer;
}




