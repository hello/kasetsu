#include "gtest/gtest.h"
#include <gsl/gsl_randist.h>
#include "HiddenMarkovModel.h"
#include "AllModels.h"
#include "CompositeModel.h"
#include <random>

class TestHmm : public ::testing::Test {
protected:
    virtual void SetUp() {
        
    }
    
    virtual void TearDown() {
        
    }
    
    
};

static int getRandomInt(const float threshold) {
    const float r = static_cast <float> (rand()) / static_cast <float> (RAND_MAX);
    
    if (r > threshold) {
        return 1;
    }
    else {
        return 0;
    }
}

TEST_F(TestHmm,TestHmm) {
    
    const gsl_rng_type * T;
    gsl_rng * r;
    
    gsl_rng_env_setup ();
    
    T = gsl_rng_default;
    r = gsl_rng_alloc (T);
    
    HmmDataVec_t poissonmeas;
    HmmDataVec_t gammameas;
    HmmDataVec_t alphabetmeas;

    
    poissonmeas.reserve(100000);
    gammameas.reserve(100000);
    alphabetmeas.reserve(100000);
    
    
    
    for (int i = 0; i < 100; i++) {
        for (int j = 0; j < 10; j++) {
            poissonmeas.push_back(gsl_ran_poisson(r, 1.0));
            gammameas.push_back(gsl_ran_gamma(r, 0.8, 0.3));
            alphabetmeas.push_back(getRandomInt(0.8));
        }
    
        for (int j = 0; j < 10; j++) {
            poissonmeas.push_back(gsl_ran_poisson(r, 3.0));
            gammameas.push_back(gsl_ran_gamma(r, 2.0, 0.8));
            alphabetmeas.push_back(getRandomInt(0.3));

        }
    }
    
    HmmDataMatrix_t A;
    A.resize(2);
    A[0] << 0.9,0.1;
    A[1] << 0.1,0.9;
    
    HmmDataMatrix_t meas;
    meas.push_back(poissonmeas);
    meas.push_back(gammameas);
    meas.push_back(alphabetmeas);
    
    HiddenMarkovModel hmm(A);
    
    {
        CompositeModel * model1 = new CompositeModel();
        CompositeModel * model2 = new CompositeModel();
        
        HmmDataVec_t probs1,probs2;
        probs1 << 0.5,0.5;
        probs2 << 0.5,0.5;
        

        model1->addModel(new PoissonModel(0,1.0) );
        model1->addModel(new GammaModel(1,.09,.16));
        model1->addModel(new AlphabetModel(2,probs1,true));

    
        model2->addModel(new PoissonModel(0,3.0));
        model2->addModel(new GammaModel(1,1.6,1.13));
        model2->addModel(new AlphabetModel(2,probs2,true));

        
        hmm.addModelForState(model1);
        hmm.addModelForState(model2);
    }

    
    for (int i = 0; i < 10; i++) {
        ReestimationResult_t res = hmm.reestimate(meas);
        std::cout << res.getLogLikelihood() << std::endl;
    }
    
    

    
    gsl_rng_free(r);

    

}

