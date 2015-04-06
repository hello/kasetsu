#include "gtest/gtest.h"

#include "AllModels.h"
#include <cmath>

class TestModels : public ::testing::Test {
protected:
    virtual void SetUp() {
        
    }
    
    virtual void TearDown() {
        
    }
    
    
};


TEST_F(TestModels,TestPoisson) {
    PoissonModel model1(0,1.1);
    PoissonModel model2(1,0.7);
 
    HmmDataMatrix_t mtx;
    HmmDataVec_t vec1;
    vec1.push_back(0);
    vec1.push_back(1);
    vec1.push_back(2);
    

    HmmDataVec_t vec2;
    vec2.push_back(2);
    vec2.push_back(3);
    vec2.push_back(4);
    
    mtx.push_back(vec1);
    mtx.push_back(vec2);
    
    HmmDataVec_t res1 = model1.getLogOfPdf(mtx);
    HmmDataVec_t res2 = model2.getLogOfPdf(mtx);
    
    const float ref1[] = {-1.1       , -1.00468982, -1.60252682};
    const float ref2[] = {-2.10649707, -3.5617843 , -5.30475361};
    
    for (int i = 0; i < 3; i++) {
        ASSERT_FLOAT_EQ(ref1[i], res1[i]);
        ASSERT_FLOAT_EQ(ref2[i], res2[i]);
    }
    

}

