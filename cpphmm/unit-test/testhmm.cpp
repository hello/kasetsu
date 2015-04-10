#include "gtest/gtest.h"
#include <gsl/gsl_randist.h>
#include "HiddenMarkovModel.h"
#include "AllModels.h"
#include "CompositeModel.h"

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
    
    std::vector<HmmFloat_t> poissonmeas;
    std::vector<HmmFloat_t> gammameas;

    
    poissonmeas.reserve(100000);
    gammameas.reserve(100000);
    
    for (int i = 0; i < 1000; i++) {
        for (int j = 0; j < 50; j++) {
            poissonmeas.push_back(gsl_ran_poisson(r, 1.0));
            gammameas.push_back(gsl_ran_gamma(r, 1.0, 1.0/2.0));
        }
    
        for (int j = 0; j < 100; j++) {
            poissonmeas.push_back(gsl_ran_poisson(r, 3.0));
            gammameas.push_back(gsl_ran_gamma(r, 2.0, 1.0/3.0));

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
    meas.push_back(gammameas);
    
    HiddenMarkovModel hmm(A);
    
    {
        CompositeModel * model1 = new CompositeModel();
        CompositeModel * model2 = new CompositeModel();

        model1->addModel(new PoissonModel(0,0.5) );
        model1->addModel(new GammaModel(1,1.0,1.0));
    
        model2->addModel(new PoissonModel(0,1.0));
        model2->addModel(new GammaModel(1,2.0,1.0));
        
        hmm.addModelForState(model1);
        hmm.addModelForState(model2);
    }

    
    for (int i = 0; i < 10; i++) {
        hmm.reestimate(meas);
    }
    
    

    
    gsl_rng_free(r);

    

}

