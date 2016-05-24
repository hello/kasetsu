#ifndef _TINYLSTM_MATH_H_
#define _TINYLSTM_MATH_H_

#include "tinylstm_types.h"

#ifdef __cplusplus
extern "C" {
#endif

#define QFIXEDPOINT (7)
    
#define TOFIX(x)\
        (Weight_t)(x * (1 << QFIXEDPOINT))

Weight_t tinylstm_tanh(WeightLong_t x);
void tinylstm_vec_tanh(Weight_t * out, const WeightLong_t * in, const uint32_t num_elements);

void tinylstm_matmulvec_long_output(WeightLong_t * out,const Weight_t * mat, const Weight_t * vec, const uint32_t num_rows, const uint32_t num_cols);

void tinylstm_convolve3d_direct(Weight_t * out, const Weight_t * weights,const Weight_t * image, const Weight_t bias,const uint32_t num_weights_rows,const uint32_t num_weights_cols, const uint32_t num_image_rows, const uint32_t num_image_cols,const uint32_t num_images);
    
#define MATMULVEC_LONG_OUTPUT(out,mat,vec,numrows,numcols) \
    tinylstm_matmulvec_long_output(out,mat,vec,numrows,numcols)

#ifdef __cplusplus
}
#endif

#endif
