#include "gtest/gtest.h"
#include "../tinylstm_types.h"
#include "../tinylstm_math.h"
#include "../tinylstm_conv_layer.h"
#include "../tinylstm_tensor.h"
#include "weights1.c"
#include "biases1.c"
#include "image.c"
#include "ref1.c"

const static ConvLayer2D_t conv_layer_def = {&weights1,&biases1,ref1_dims,image_dims};

class TestConv : public ::testing::Test {
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

class DISABLED_Test1 : public TestConv {};


TEST_F(TestConv, Test3DConv) {
  //  tinylstm_convolve3d_direct(
}

TEST_F(TestConv,TestConvLayer) {

    tensor_in = tinylstm_create_new_tensor(image_dims);


    ConstLayer_t layer = tinylstm_create_conv_layer(&conv_layer_def);
    
    uint32_t output_dims[TENSOR_DIM];
    layer.get_output_dims(layer.context,output_dims);
    
    
    tensor_out = tinylstm_create_new_tensor(output_dims);

    layer.eval(layer.context,tensor_out,tensor_in);

    uint32_t out_size = tensor_out->dims[0] * tensor_out->dims[1] * tensor_out->dims[2] * tensor_out->dims[3];
    ASSERT_TRUE(out_size == ref1_dims[0]*ref1_dims[1]*ref1_dims[2] * ref1_dims[3]);
    
    for (uint32_t i = 0; i < out_size; i++) {
        int diff = ref1_weights[i] - tensor_out->x[i];
        
        if (abs(diff) > 5) {
            std::cout << "diff was " << diff << std::endl;
            ASSERT_TRUE(false);
        }
    }


    
}

