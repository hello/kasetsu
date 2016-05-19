#ifndef _TINYLSTM_TYPES_H_
#define _TINYLSTM_TYPES_H_
#include <stdint.h>

#ifdef __cplusplus
extern "C" {
#endif



typedef int8_t Weight_t;
typedef Weight_t Data_t;
typedef int16_t WeightLong_t;
typedef Weight_t (*SquashFunc_t)(WeightLong_t x);
typedef void (*ActionCallback_t)(void *);
    
#ifdef __cplusplus
}
#endif



#endif //_TINYLSTM_TYPES_H_
