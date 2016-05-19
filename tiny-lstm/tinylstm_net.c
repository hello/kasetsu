#include "tinylstm_net.h"
#include "tinylstm_math.h"
#include <assert.h>

static void  evaluate_full(Element_t * pFull,const Data_t * input,Data_t * output) {
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
    uint32_t i;
    for (iunit = 0; iunit < n_units; iunit++) {
        
        const Weight_t * w = weights + iunit*matsize;
        const Data_t * x = input + iunit*n_in;
        Data_t * out = output + iunit * n_out;
        
        MATMULVEC_LONG_OUTPUT(tempOut,w,x,n_out,n_in);
        
        for (i = 0; i < n_out; i++) {
            *(out + i) = squash(tempOut[i]);
        }
        
    }
    
}