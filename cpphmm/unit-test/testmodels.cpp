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
    PoissonModel model1(0,1.1,1.0);
    PoissonModel model2(1,0.7,1.0);
 
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

TEST_F(TestModels, TestGamma) {
    GammaModel model1(0,0.8,0.6,1.0);
    GammaModel model2(1,2.0,1.3,1.0);
    
    HmmDataMatrix_t mtx;
    HmmDataVec_t vec1;
    vec1.push_back(0.1);
    vec1.push_back(1.2);
    vec1.push_back(2.4);
    
    
    HmmDataVec_t vec2;
    vec2.push_back(2.2);
    vec2.push_back(3.3);
    vec2.push_back(4.4);
    
    mtx.push_back(vec1);
    mtx.push_back(vec2);
    
    HmmDataVec_t res1 = model1.getLogOfPdf(mtx);
    HmmDataVec_t res2 = model2.getLogOfPdf(mtx);
    
    const float ref1[] = {-0.51631842, -1.02805769, -3.15560989};
    const float ref2[] = {-1.3227215 , -2.07028103, -2.97883393};
    
    for (int i = 0; i < 3; i++) {
        ASSERT_FLOAT_EQ(ref1[i], res1[i]);
        ASSERT_FLOAT_EQ(ref2[i], res2[i]);
    }
    
}


TEST_F(TestModels, TestGaussian) {
    OneDimensionalGaussianModel model1(0,0.8,0.6,1.0);
    OneDimensionalGaussianModel model2(1,-0.3,1.3,1.0);
    
    HmmDataMatrix_t mtx;
    HmmDataVec_t vec1;
    vec1.push_back(0.1);
    vec1.push_back(1.2);
    vec1.push_back(-2.4);
    
    
    HmmDataVec_t vec2;
    vec2.push_back(2.2);
    vec2.push_back(3.3);
    vec2.push_back(-4.4);
    
    mtx.push_back(vec1);
    mtx.push_back(vec2);
    
    HmmDataVec_t res1 = model1.getLogOfPdf(mtx);
    HmmDataVec_t res2 = model2.getLogOfPdf(mtx);
    
    const float ref1[] = {-1.08866846,  -0.63033513, -14.63033513};
    const float ref2[] = {-3.03041522, -5.01562232, -6.15467558};
    
    for (int i = 0; i < 3; i++) {
        ASSERT_FLOAT_EQ(ref1[i], res1[i]);
        ASSERT_FLOAT_EQ(ref2[i], res2[i]);
    }
    
}

TEST_F(TestModels, TestMultivariateGaussian) {
    HmmDataMatrix_t P;
    P.resize(2);
    
    P[0] << 1.56762006,  0.09054419;
    P[1] << 0.09054419,  1.09772478;
    
    HmmDataVec_t mu;
    mu << 0.1,0.2;
    
    UIntVec_t obsnums;
    obsnums << 0,1;
    
    MultivariateGaussian mvg(obsnums,mu,P,0.0001,1.0);
    
    HmmDataMatrix_t obs;
    obs.resize(2);
    obs[0] << 0.1,1.0,2.0;
    obs[1] << 0.2,-0.1,0.5;
    
    HmmDataVec_t ref;
    ref << -2.1068884129062497,-2.4219432836910, -3.2748820631329;
    
    HmmDataVec_t evals = mvg.getLogOfPdf(obs);
    
    for (int i = 0; i < 2; i++) {
        ASSERT_FLOAT_EQ(ref[i], evals[i]);
    }
    
}





