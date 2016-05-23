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
    
#ifdef __cplusplus
}
#endif



#endif //_TINYLSTM_TYPES_H_
