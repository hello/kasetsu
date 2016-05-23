#ifndef _TINYLSTM_TYPES_H_
#define _TINYLSTM_TYPES_H_
#include <stdint.h>

#ifdef __cplusplus
extern "C" {
#endif



typedef int8_t Weight_t;
typedef Weight_t Data_t; //data and weight are the same for now
typedef int16_t WeightLong_t;
    
//callback defs
typedef void (*SquashFunc_t)(Weight_t * out, const WeightLong_t * in, const uint32_t num_elements);
typedef void (*ActionCallback_t)(void *);
    

#define TENSOR_DIM (3)

/*
      TENSOR DEFS
 */
typedef void(*TensorDelete_t)(void * context);

typedef struct{
    Weight_t * x;
    uint32_t dims[TENSOR_DIM];
    TensorDelete_t free;
} Tensor_t;
    
typedef struct{
    const Weight_t * x;
    const uint32_t dims[TENSOR_DIM];
} ConstTensor_t;

    typedef union {
        ConstTensor_t const_tensor;
        Tensor_t tensor;
    } ;
    
/*
      LAYER DEFS
 */
typedef void (*LayerEval_t)(void * context,Tensor_t * out,const Tensor_t * in);

typedef uint32_t (*LayerSize_t)(void * context);

typedef void (*LayerDelete_t)(void * context);


typedef struct {
    LayerEval_t eval;
    LayerSize_t get_output_size_bytes;
    LayerDelete_t free;
    void * context;
} Layer_t;

    
#ifdef __cplusplus
}
#endif



#endif //_TINYLSTM_TYPES_H_
