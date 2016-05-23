#include "tinylstm_tensor.h"
#include "tinylstm_memory.h"

void delete_tensor(void * context) {
    Tensor_t * p = (Tensor_t *) context;
    
    FREE(p->x);
    FREE(p);
}

Tensor_t * tinylstm_create_new_tensor(const uint32_t size_of_weights_in_bytes,const uint32_t dims[3]) {
    Tensor_t * tensor = (Tensor_t *)MALLLOC(sizeof(Tensor_t));
    MEMSET(tensor,0,sizeof(Tensor_t));
    MEMCPY(tensor->dims, dims, sizeof(tensor->dims));
    tensor->x = MALLLOC(size_of_weights_in_bytes);
    tensor->free = delete_tensor;
    return tensor;
}

