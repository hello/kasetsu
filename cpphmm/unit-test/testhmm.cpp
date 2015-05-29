#include "gtest/gtest.h"
#include <gsl/gsl_randist.h>
#include "HiddenMarkovModel.h"
#include "AllModels.h"
#include "CompositeModel.h"
#include <random>
#include "signalgenerator.h"
#include <fstream>

class TestHmm : public ::testing::Test {
public:
    TestHmm() {
        gsl_rng_env_setup ();
    }
    
protected:
    
    gsl_rng * _r;
    
    virtual void SetUp() {
        _r = gsl_rng_alloc (gsl_rng_default);
    }
    
    virtual void TearDown() {
        gsl_rng_free(_r);

    }
    
    int getRandomInt(const float threshold) {
        const float r = static_cast <float> (rand()) / static_cast <float> (RAND_MAX);
        
        if (r > threshold) {
            return 1;
        }
        else {
            return 0;
        }
    }

    
    HmmDataMatrix_t getRandom2StateMeas() {
        HmmDataVec_t poissonmeas;
        HmmDataVec_t gammameas;
        HmmDataVec_t alphabetmeas;
        
        
        poissonmeas.reserve(100000);
        gammameas.reserve(100000);
        alphabetmeas.reserve(100000);
        
        float mode1TransitionProb = 0.1;
        float mode2TransitionProb = 0.2;
        bool isMode1 = true;
        
        for (int i = 0; i < 1000; i++) {
            if (isMode1) {
                poissonmeas.push_back(gsl_ran_poisson(_r, 1.0));
                gammameas.push_back(gsl_ran_gamma(_r, 0.8, 0.3));
                alphabetmeas.push_back(getRandomInt(0.8));
                
                if (getRandomInt(1.0 - mode1TransitionProb)) {
                    isMode1 = false;
                }
                
            }
            else {
                poissonmeas.push_back(gsl_ran_poisson(_r, 3.0));
                gammameas.push_back(gsl_ran_gamma(_r, 2.0, 0.8));
                alphabetmeas.push_back(getRandomInt(0.3));
                
                if (getRandomInt(1.0 - mode2TransitionProb)) {
                    isMode1 = true;
                }
            }
        }
        
        HmmDataMatrix_t meas;
        meas.push_back(poissonmeas);
        meas.push_back(gammameas);
        meas.push_back(alphabetmeas);
        
        return meas;
    }
    
    
};

class DISABLED_TestHmm : public TestHmm {
    
};

TEST_F(TestHmm,TestHmm) {
    
   
    const HmmDataMatrix_t meas = getRandom2StateMeas();
    
    HmmDataMatrix_t A;
    A.resize(2);
    A[0] << 0.9,0.1;
    A[1] << 0.1,0.9;
    

    
    HiddenMarkovModel hmm(A);
    
    {
        CompositeModel * model1 = new CompositeModel();
        CompositeModel * model2 = new CompositeModel();
        
        HmmDataVec_t probs1,probs2;
        probs1 << 0.5,0.5;
        probs2 << 0.5,0.5;
        

        model1->addModel(HmmPdfInterfaceSharedPtr_t(new PoissonModel(0,1.0,1.0) ));
        model1->addModel(HmmPdfInterfaceSharedPtr_t(new GammaModel(1,.09,.16,1.0)));
        model1->addModel(HmmPdfInterfaceSharedPtr_t(new AlphabetModel(2,probs1,true,1.0)));

    
        model2->addModel(HmmPdfInterfaceSharedPtr_t(new PoissonModel(0,3.0,1.0)));
        model2->addModel(HmmPdfInterfaceSharedPtr_t(new GammaModel(1,1.6,1.13,1.0)));
        model2->addModel(HmmPdfInterfaceSharedPtr_t(new AlphabetModel(2,probs2,true,1.0)));

        
        hmm.addModelForState(HmmPdfInterfaceSharedPtr_t(model1));
        hmm.addModelForState(HmmPdfInterfaceSharedPtr_t(model2));
    }

    
    for (int i = 0; i < 3; i++) {
        ReestimationResult_t res = hmm.reestimateViterbi(meas);
        std::cout << res.getLogLikelihood() << std::endl;
    }
    
    for (int i = 0; i < 8; i++) {
        ReestimationResult_t res = hmm.reestimate(meas);
        std::cout << res.getLogLikelihood() << std::endl;
    }
    
    
    //std::string serializedString = hmm.serializeToJson();
    //std::cout <<serializedString << std::endl;


}

TEST_F(TestHmm,TestGammaWithManyStates) {
    ReestimationResult_t res;
    HmmDataVec_t means;
    HmmDataVec_t stddevs;
    
    
    means << 1.0,2.0,3.0,4.0;
    stddevs << 0.1,0.1,0.1,0.1;
    
    HmmDataMatrix_t A;
    A.resize(4);
    
    A[0] << 0.5,0.25,0.25,0.0;
    A[1] << 0.2,0.2,0.3,0.3;
    A[2] << 0.1,0.2,0.5,0.2;
    A[3] << 0.1,0.0,0.0,0.9;
    
    const HmmDataVec_t measvec = getGammaSignal(100000,A,means,stddevs);
    
    
    
    
    HmmDataMatrix_t meas;
    meas.push_back(measvec);
    
    
   /* std::ofstream fileout("foo.csv");
    fileout << measvec;
    fileout.close();
    */
    
    
    HmmDataMatrix_t Ainit;
    Ainit.resize(4);
    
    Ainit[0] << 0.20,0.30,0.40,0.10;
    Ainit[1] << 0.30,0.20,0.20,0.30;
    Ainit[2] << 0.30,0.20,0.30,0.20;
    Ainit[3] << 0.15,0.15,0.50,0.20;
    
    GammaModel model(0, 0.5, 0.5,1.0);
    
    HiddenMarkovModel hmm(Ainit);
    
    hmm.addModelForState(model.clone(true));
    hmm.addModelForState(model.clone(true));
    hmm.addModelForState(model.clone(true));
    hmm.addModelForState(model.clone(true));


    
    for (int iter = 0; iter < 20; iter++) {
      //  res = hmm.reestimateViterbi(meas);
        res = hmm.reestimate(meas);
        std::cout << res.getLogLikelihood() << std::endl;

    }
    
   
    
    int foo = 3;
    foo++;

    
    
    
}

TEST_F(TestHmm,TestPoissonWithManyStates) {
    ReestimationResult_t res;
    HmmDataVec_t means;
    HmmDataVec_t stddevs;
    
    
    means << 1.0,5.0,20.0;
    
    HmmDataMatrix_t A;
    A.resize(3);
    
    A[0] << 0.80,0.10,0.10;
    A[1] << 0.30,0.60,0.10;
    A[2] << 0.20,0.20,0.60;
    
    const HmmDataVec_t measvec = getPoissonSignal(100000,A,means);
    
    
    
    
    HmmDataMatrix_t meas;
    meas.push_back(measvec);
    
    
    /* std::ofstream fileout("foo.csv");
     fileout << measvec;
     fileout.close();
     */
    
    
    HmmDataMatrix_t Ainit;
    Ainit.resize(3);
    
    Ainit[0] << 0.8,0.15,0.05;
    Ainit[1] << 0.3,0.6,0.1;
    Ainit[2] << 0.2,0.2,0.6;
    
    
    HiddenMarkovModel hmm(Ainit);
    
    hmm.addModelForState(HmmPdfInterfaceSharedPtr_t(new PoissonModel(0,1.1,1.0)));
    hmm.addModelForState(HmmPdfInterfaceSharedPtr_t(new PoissonModel(0,5.5,1.0)));
    hmm.addModelForState(HmmPdfInterfaceSharedPtr_t(new PoissonModel(0,20.5,1.0)));

    
    
    for (int iter = 0; iter < 30; iter++) {
        //  res = hmm.reestimateViterbi(meas);
        res = hmm.reestimate(meas);
        std::cout << res.getLogLikelihood() << std::endl;
        
    }
    
    
    std::cout << hmm.serializeToJson() << std::endl;
    
    int foo = 3;
    foo++;
    
    
    
    
}

TEST_F(TestHmm, TestVSTACS) {
    ReestimationResult_t res;
    HmmDataVec_t means;
    HmmDataVec_t stddevs;
    
    
    means << 1.0,2.0,3.0,2.0;
    stddevs << 0.1,0.1,0.1,0.1;
    
    HmmDataMatrix_t A;
    A.resize(4);
    
    A[0] << 0.8,0.2,0.0,0.0;
    A[1] << 0.00,0.90,0.10,0.0;
    A[2] << 0.0,0.0,0.8,0.2;
    A[3] << 0.6,0.0,0.0,0.4;
    
    const HmmDataVec_t measvec = getGammaSignal(100000,A,means,stddevs);
    
    
    
    
    HmmDataMatrix_t meas;
    meas.push_back(measvec);
    
    
    /* std::ofstream fileout("foo.csv");
     fileout << measvec;
     fileout.close();
     */
    
    
    HmmDataMatrix_t Ainit;
    Ainit.resize(3);
    
    Ainit[0] << 0.8,0.2,0.0;
    Ainit[1] << 0.1,0.8,0.1;
    Ainit[2] << 0.0,0.2,0.8;
   
    
    GammaModel model1(0, 1, 0.1,1.0);
    GammaModel model2(0, 2, 0.1,1.0);
    GammaModel model3(0, 3, 0.1,1.0);

    HiddenMarkovModel hmm(Ainit);
    
    hmm.addModelForState(model1.clone(false));
    hmm.addModelForState(model2.clone(false));
    hmm.addModelForState(model3.clone(false));
    
    
    hmm.enlargeWithVSTACS(meas, 1);
    
    std::cout << hmm.serializeToJson() << std::endl;
    int foo = 3;
    foo++;


}

