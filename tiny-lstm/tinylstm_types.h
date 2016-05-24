#ifndef _TINYLSTM_TYPES_H_
#define _TINYLSTM_TYPES_H_
#include <stdint.h>

#ifdef __cplusplus
extern "C" {
#endif

#define MAX_WEIGHT (0x7F)

typedef int8_t Weight_t;
typedef Weight_t Data_t; //data and weight are the same for now
typedef int16_t WeightLong_t;
    
//callback defs
typedef void (*SquashFunc_t)(Weight_t * out, const WeightLong_t * in, const uint32_t num_elements);
typedef void (*ActionCallback_t)(void *);
    

#define TENSOR_DIM (4)

/*
      TENSOR DEFS
 */
typedef void(*TensorDelete_t)(void * context);

typedef struct{
    Weight_t * x;
    uint32_t dims[TENSOR_DIM];
    TensorDelete_t delete_me;
} Tensor_t;
    
typedef struct{
    const Weight_t * x;
    const uint32_t dims[TENSOR_DIM];
} ConstTensor_t;

/*
      LAYER DEFS
 */
typedef void (*ConstLayerEval_t)(const void * context,Tensor_t * out,const Tensor_t * in);

typedef void (*ConstLayerDims_t)(const void * context,uint32_t * dims);

typedef struct {
    ConstLayerEval_t eval;
    ConstLayerDims_t get_output_dims;
    const void * context;
} ConstLayer_t;

    
#ifdef __cplusplus
}
#endif



#endif //_TINYLSTM_TYPES_H_
