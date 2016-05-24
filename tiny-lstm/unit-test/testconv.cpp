#include "gtest/gtest.h"
#include "../tinylstm_types.h"
#include "../tinylstm_math.h"
#include "../tinylstm_conv_layer.h"
#include "../tinylstm_tensor.h"

class Test1 : public ::testing::Test {
protected:
    virtual void SetUp() {
        
    }
    
    virtual void TearDown() {
        
    }
    
    
};

class DISABLED_Test1 : public Test1 {};

TEST_F(Test1,TestFOO) {
    const static Weight_t weights[4] = {TOFIX(0.5),TOFIX(0.5),TOFIX(0.5),TOFIX(0.5)};
    const static Weight_t biases[1] = {TOFIX(0.0)};
    const static ConstTensor_t weight_tensor = {&weights[0],{1,1,2,2}};
    const static ConstTensor_t bias_tensor = {&biases[0],{1,1,1,1}};

    const static ConvLayer2D_t layer_def = {&weight_tensor,&bias_tensor,{1,1,3,3},{1,1,4,4}};
    
    //on stack
    ConstLayer_t layer = tinylstm_create_conv_layer(&layer_def);
    
    const uint32_t dims[TENSOR_DIM] = {1,1,3,3};
    Tensor_t * tensor_out = tinylstm_create_new_tensor(dims);
    
    const uint32_t dims2[TENSOR_DIM] = {1,1,4,4};
    Tensor_t * tensor_in = tinylstm_create_new_tensor(dims2);
    
    for (uint32_t islice = 0; islice < 1; islice++) {
        Weight_t * p = tensor_in->x;
        
        for (uint32_t j = 0; j < 4; j++) {
            for (uint32_t i = 0; i < 4; i++) {
                *(p + j*4 + i) = TOFIX(0.25);
            }
        }
    }
    
    layer.eval(layer.context,tensor_out,tensor_in);
    
    
    
    tensor_in->delete_me(tensor_in);
    tensor_out->delete_me(tensor_out);

    
}

