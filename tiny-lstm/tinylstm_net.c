#include "tinylstm_net.h"
#include "tinylstm_math.h"
#include "tinylstm_memory.h"
#include "tinylstm_tensor.h"
#include <assert.h>


typedef struct {
    const Tensor_t * weights;
    const uint32_t input_dims[3];
    const uint32_t output_dims[3];

} ConvLayer2D_t;


uint32_t get_conv2d_output_size(void * context) {
    const ConvLayer2D_t * layer = (ConvLayer2D_t *)context;
    return layer->output_dims[0]*layer->output_dims[1]*layer->output_dims[2] * sizeof(Weight_t);
}

void eval_conv2d_direct(void * context,Tensor_t * out,const Tensor_t * in) {
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






Tensor_t * eval_net(const SequentialNetwork_t * net,Tensor_t * input) {

    Tensor_t * current_input = input;
    Tensor_t * current_output = NULL;
    
    for (uint32_t ilayer = 0; ilayer < net->num_layers; ilayer++) {
        const Layer_t * const layer = &net->layers[ilayer];
        const uint32_t layer_output_size = layer->get_output_size_bytes(layer->context);
        const uint32_t new_layer_dims[TENSOR_DIM] = {0,0,0};
        
        //allocate output
        current_output = tinylstm_create_new_tensor(layer_output_size,new_layer_dims);

        //perform evaluation
        layer->eval(layer->context,current_output,current_input);
        
        //output becomes new input --- so delete input if we can
        if (current_input->delete) {
            current_input->delete(current_input);
        }

        current_input = current_output;
    }
    
    return current_output;
    
}


/*
Layer_t * create_1d_conv_layer(const Weight_t * weights, const uint32_t conv_width, const uint32_t num_convs) {
    
    
    
}
 */











/*
  does squash(W*x) for each unit (each "unit" is the "slice", 3rd dimension of your data tensor, etc.)
 */
/*
void  tinylstm_evaluate_full(Element_t * pFull,const Data_t * input,Data_t * output) {
    assert(pFull->squash_function);
    assert(pFull->num_outputs_per_unit < MAX_OUTPUT_SIZE);

    const Weight_t * weights = pFull->weights;
    const uint32_t n_in = pFull->num_inputs_per_unit;
    const uint32_t n_out = pFull->num_outputs_per_unit;
    const uint32_t n_units = pFull->num_units;
    WeightLong_t tempOut[MAX_OUTPUT_SIZE];
    const SquashFunc_t squash = pFull->squash_function;
    
    const uint32_t matsize = n_in * n_out;
    uint32_t iunit;
    for (iunit = 0; iunit < n_units; iunit++) {
        
        const Weight_t * w = weights + iunit*matsize;
        const Data_t * x = input + iunit*n_in;
        Data_t * out = output + iunit * n_out;
        
        MATMULVEC_LONG_OUTPUT(tempOut,w,x,n_out,n_in);
        
        squash(out,tempOut,n_out);
        
    }
    
}

/*
 

 void tinylstm_evaluate_conv_1d(Element_t * pConv,const Data_t * input,Data_t * output) {

     assert(pConv->squash_function);
     assert(pConv->num_outputs_per_unit < MAX_OUTPUT_SIZE);
     
     const Weight_t * weights = pConv->weights;
     const uint32_t n_in = pConv->num_inputs_per_unit;
     const uint32_t n_out = pConv->num_outputs_per_unit;
     const uint32_t n_units = pConv->num_units;
     const uint32_t n_conv = n_out - n_in + 1;
     WeightLong_t tempOut[MAX_OUTPUT_SIZE];

     
     //weights is n_units rows by n_conv cols
     
 }

*/