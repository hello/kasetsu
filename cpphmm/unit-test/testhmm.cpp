#include "gtest/gtest.h"
#include <gsl/gsl_randist.h>
#include "HiddenMarkovModel.h"
#include "AllModels.h"

class TestHmm : public ::testing::Test {
protected:
    virtual void SetUp() {
        
    }
    
    virtual void TearDown() {
        
    }
    
    
};


TEST_F(TestHmm,TestHmm) {
    
    const gsl_rng_type * T;
    gsl_rng * r;
    
    gsl_rng_env_setup ();
    
    T = gsl_rng_default;
    r = gsl_rng_alloc (T);
    
    int idx = 0;
    std::vector<float> poissonmeas;
    
    poissonmeas.reserve(10000);
    
    for (int i = 0; i < 100; i++) {
        for (int j = 0; j < 10; j++) {
            poissonmeas.push_back(gsl_ran_poisson(r, 1.0));
        }
    
        for (int j = 0; j < 20; j++) {
            poissonmeas.push_back(gsl_ran_poisson(r, 3.0));
        }
    }
    
    HmmDataMatrix_t A;
    
    HmmDataVec_t a1;
    a1.push_back(0.5);
    a1.push_back(0.5);

    HmmDataVec_t a2;
    a2.push_back(0.5);
    a2.push_back(0.5);
    
    A.push_back(a1);
    A.push_back(a2);
    
    HmmDataMatrix_t meas;
    meas.push_back(poissonmeas);
    
    HiddenMarkovModel hmm(A);
    
    hmm.addModelForState(new PoissonModel(0,0.5));
    hmm.addModelForState(new PoissonModel(0,1.0));

    
    for (int i = 0; i < 50; i++) {
        hmm.reestimate(meas);
    }
    
    

    
    gsl_rng_free(r);

    

}

