#ifndef _TINY_LSTM_TENSOR_H_
#define _TINY_LSTM_TENSOR_H_

#include "tinylstm_types.h"

#ifdef __cplusplus
extern "C" {
#endif

/* MEMORY LAYOUT OF THE "TENSOR"
 
    A SERIES OF 2-D MATRICES
 
    A 2-D MATRIX IS row1,row2,row3,.....  
    THE STRIDE IS THE NUMBER OF COLUMNS
 
    so for the 3D matrix, a.k.a the tensor
    the stride is NCOLS * NROWS
 
    mat1_row1, mat1_row2... mat2_row1, mat2_row2.... matN_rowM
 
 */


    

inline Weight_t * get_slice(Tensor_t * tensor, uint32_t nslice) {
    const uint32_t stride = tensor->dims[2] * tensor->dims[1];
    return tensor->x + stride * nslice;
}

    
Tensor_t * tinylstm_create_new_tensor(const uint32_t dims[3]);


#ifdef __cplusplus
}
#endif

#endif // _TINY_LSTM_TENSOR_H_
