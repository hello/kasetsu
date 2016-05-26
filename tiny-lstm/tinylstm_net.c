#include "tinylstm_net.h"
#include "tinylstm_math.h"
#include "tinylstm_tensor.h"
#include <assert.h>




Tensor_t * eval_net(const ConstSequentialNetwork_t * net,Tensor_t * input) {

    Tensor_t * current_input = input;
    Tensor_t * current_output = 0;
    
    for (uint32_t ilayer = 0; ilayer < net->num_layers; ilayer++) {
        const ConstLayer_t * const layer = &net->layers[ilayer];
        
        uint32_t output_dims[TENSOR_DIM];
        layer->get_output_dims(layer->context,&output_dims[0]);
        
        //allocate output
        current_output = tinylstm_create_new_tensor(output_dims);

        //perform evaluation
        layer->eval(layer->context,current_output,current_input);
        
        //output becomes new input --- so delete input if we can
        if (current_input->delete_me) {
            current_input->delete_me(current_input);
        }

        current_input = current_output;
    }
    
    //whomever received this object must delete it
    return current_output;
    
}


