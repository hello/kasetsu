#include "gtest/gtest.h"
#include "../tinylstm_types.h"
#include "../tinylstm_math.h"
#include "../tinylstm_conv_layer.h"
#include "../tinylstm_tensor.h"


class TestFull : public ::testing::Test {
protected:
    
    
    virtual void SetUp() {
        tensor_in = NULL;
        tensor_out = NULL;
    }
    
    virtual void TearDown() {
        if (tensor_in) {
            tensor_in->delete_me(tensor_in);
        }
        
        if (tensor_out) {
            tensor_out->delete_me(tensor_out);
        }
    }
    
    Tensor_t * tensor_in;
    Tensor_t * tensor_out;
    
};

class DISABLED_Test1 : public TestFull {};


TEST_F(TestFull, TestFOO) {
  //  tinylstm_convolve3d_direct(
}

