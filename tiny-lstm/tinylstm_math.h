#ifndef _TINYLSTM_MATH_H_
#define _TINYLSTM_MATH_H_

#include "tinylstm_types.h"

#ifdef __cplusplus
extern "C" {
#endif

Weight_t tinylstm_tanh(WeightLong_t x);

void tinylstm_matmulvec_long_output(WeightLong_t * out,const Weight_t * mat, const Weight_t * vec, const uint32_t num_rows, const uint32_t num_cols);

#define MATMULVEC_LONG_OUTPUT(out,mat,vec,numrows,numcols) \
    tinylstm_matmulvec_long_output(out,mat,vec,numrows,numcols)

#ifdef __cplusplus
}
#endif

#endif
