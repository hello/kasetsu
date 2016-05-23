#include "tinylstm_tensor.h"
#include "tinylstm_memory.h"

void delete_tensor(void * context) {
    Tensor_t * p = (Tensor_t *) context;
    
    FREE(p->x);
    FREE(p);
}

Tensor_t * tinylstm_create_new_tensor(const uint32_t num_elements,const uint32_t dims[3]) {
    Tensor_t * tensor = (Tensor_t *)MALLLOC(sizeof(Tensor_t));
    MEMSET(tensor,0,sizeof(Tensor_t));
    MEMCPY(tensor->dims, dims, sizeof(tensor->dims));
    tensor->x = MALLLOC(num_elements * sizeof(Weight_t));
    tensor->delete_me = delete_tensor;
    return tensor;
}

