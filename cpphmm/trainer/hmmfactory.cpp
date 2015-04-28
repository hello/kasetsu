#include "hmmfactory.h"
#include <string>
#include "CompositeModel.h"
#include "AllModels.h"
#include <iostream>

static HmmPdfInterface * getDefaultModelForState(float lightGammaMean, float lightGammStdDev, float movementPoissonMean, float disturbanceFraction, float soundcountGammaMean, float soundcountGammaStdDev, float natlightPenaltyFraction,bool useNatLight = true) {
    
    
    HmmDataVec_t disturbanceProbs;
    disturbanceProbs.resize(2);
    disturbanceProbs[0] = 1.0 - disturbanceFraction;
    disturbanceProbs[1] = disturbanceFraction;
    
    HmmDataVec_t natlightProbs;
    natlightProbs.resize(2);
    natlightProbs[0] = 1.0;
    natlightProbs[1] = natlightPenaltyFraction;
    
    CompositeModel * p = new CompositeModel();
    
    p->addModel(new GammaModel(0,lightGammaMean,lightGammStdDev));
    p->addModel(new PoissonModel(1,movementPoissonMean));
    p->addModel(new AlphabetModel(2,disturbanceProbs,true));
    p->addModel(new GammaModel(3,lightGammaMean,lightGammStdDev));
    
    if (useNatLight)  {
        p->addModel(new AlphabetModel(4,natlightProbs,false));
    }
    
    return p;

}

static HiddenMarkovModel * getSingleStateModel() {
    const int num_states = 1;

    HmmDataMatrix_t A;
    
    A.resize(num_states);
    A[0] << 1.0;

    HiddenMarkovModel * model = new HiddenMarkovModel(A);

    model->addModelForState(getDefaultModelForState(1.0, 1.0, 1.0, 0.5,1.0, 1.0, 1.0,false));
    
    return model;

}


static HiddenMarkovModel * getDefaultModel() {
    const int num_states = 11;
    
    HmmDataMatrix_t A;
    
    A.resize(num_states);
    
    const float low_light = 0.1;
  //  const float med_light = 3.0;
    const float high_light = 6.0;
    const float low_light_stddev = 1.0;
    const float high_light_stddev = 2.5;
    
    const float no_motion = 0.01;
    const float low_motion = 3.0;
//    const float  med_motion = 4.0;
    const float high_motion = 8.0;
    
    const float vlow_wave = 0.01;
    const float low_wave =  0.1;
    const float high_wave = 0.9;
    
    const float sc_low = 1.0;
    const float sc_high = 2.0;
    const float sc_low_stddev = 0.5;
    const float sc_high_stddev = 1.0;
    
    const float no_penalty = 1.0;
    const float yes_penalty = 1e-6;
    
    
    A[0] << 0.65, 0.10, 0.10, 0.10,   0.10,  0.10,   0.00, 0.00, 0.00,   0.00, 0.00;
    A[1] << 0.10, 0.65, 0.10, 0.10,   0.10,  0.10,   0.00, 0.00, 0.00,   0.00, 0.00;
    A[2] << 0.10, 0.10, 0.65, 0.10,   0.10,  0.10,   0.00, 0.00, 0.00,   0.00, 0.00;
    A[3] << 0.10, 0.10, 0.10, 0.65,   0.10,  0.10,   0.00, 0.00, 0.00,   0.00, 0.00;
    
    A[4] << 0.05, 0.05, 0.05, 0.05,   0.70, 0.10,    0.10, 0.10, 0.00,   0.00, 0.00;
    A[5] << 0.05, 0.05, 0.05, 0.05,   0.10, 0.70,    0.10, 0.10, 0.00,   0.00, 0.00;
    
    A[6] << 0.00, 0.00, 0.00, 0.00,   0.00,  0.05,   0.55, 0.10, 0.05,   0.10, 0.10;
    A[7] << 0.00, 0.00, 0.00, 0.00,   0.00,  0.05,   0.45, 0.50, 0.00,   0.00, 0.00;
    A[8] << 0.10, 0.00, 0.10, 0.00,   0.05,  0.00,   0.00, 0.00, 0.65,   0.10, 0.10;
    
    A[9] << 0.10, 0.10, 0.10, 0.10,   0.00, 0.00,    0.00, 0.00, 0.05,   0.55, 0.10;
    A[10]<< 0.10, 0.10, 0.10, 0.10,   0.00, 0.00,    0.05, 0.05, 0.00,   0.10, 0.45;


    HiddenMarkovModel * model = new HiddenMarkovModel(A);

    
    model->addModelForState(getDefaultModelForState(high_light, high_light_stddev, no_motion, low_wave,sc_high, sc_high_stddev, no_penalty));
    model->addModelForState(getDefaultModelForState(low_light,  low_light_stddev,  no_motion, low_wave,sc_high, sc_high_stddev, no_penalty));
    model->addModelForState(getDefaultModelForState(high_light, high_light_stddev, no_motion, low_wave,sc_low,  sc_low_stddev,  no_penalty));
    model->addModelForState(getDefaultModelForState(low_light,  low_light_stddev,  no_motion, low_wave,sc_low,  sc_low_stddev,  no_penalty));
    
    model->addModelForState(getDefaultModelForState(high_light, high_light_stddev, high_motion, high_wave, sc_high,  sc_high_stddev,  no_penalty));
    model->addModelForState(getDefaultModelForState(low_light,  low_light_stddev,  high_motion, high_wave, sc_high,  sc_high_stddev,  no_penalty));

    model->addModelForState(getDefaultModelForState(low_light,  low_light_stddev,   low_motion, vlow_wave, sc_low,  sc_low_stddev,  no_penalty));
    model->addModelForState(getDefaultModelForState(low_light,  low_light_stddev,   low_motion, vlow_wave, sc_high, sc_high_stddev, no_penalty));
    model->addModelForState(getDefaultModelForState(high_light, high_light_stddev,  low_motion, vlow_wave, sc_low,  sc_low_stddev,  yes_penalty));

    model->addModelForState(getDefaultModelForState(high_light,  high_light_stddev, high_motion, high_wave, sc_high,  sc_high_stddev,  no_penalty));
    model->addModelForState(getDefaultModelForState(low_light,   low_light_stddev,  high_motion, high_wave, sc_high,  sc_high_stddev,  no_penalty));


    return model;
}

static HiddenMarkovModel * getTestModel() {
    const int num_states = 9;
    
    HmmDataMatrix_t A;
    
    A.resize(num_states);
    
    const float low_light = 0.1;
    //  const float med_light = 3.0;
    const float high_light = 6.0;
    const float low_light_stddev = 1.0;
    const float high_light_stddev = 2.5;
    
    const float no_motion = 0.01;
    const float low_motion = 3.0;
    //    const float  med_motion = 4.0;
    const float high_motion = 8.0;
    
    const float vlow_wave = 0.01;
    const float low_wave =  0.1;
    const float high_wave = 0.9;
    
    const float sc_low = 1.0;
    const float sc_high = 2.0;
    const float sc_low_stddev = 0.5;
    const float sc_high_stddev = 1.0;
    
    const float no_penalty = 1.0;
    const float yes_penalty = 1e-6;
    
    
    A[0] << 0.65, 0.10, 0.10,   0.10, 0.10,   0.00, 0.00,   0.00, 0.00;
    A[1] << 0.10, 0.65, 0.10,   0.10, 0.10,   0.00, 0.00,   0.00, 0.00;
    A[2] << 0.10, 0.10, 0.65,   0.10, 0.10,   0.00, 0.00,   0.00, 0.00;

    
    A[3] << 0.05, 0.05, 0.05,   0.70, 0.10,   0.10, 0.00,  0.00, 0.00;
    A[4] << 0.05, 0.05, 0.05,   0.10, 0.70,   0.10, 0.00,  0.00, 0.00;
    
    A[5] << 0.00, 0.00, 0.00,   0.00, 0.05,   0.55, 0.05,  0.10, 0.10;
    A[6] << 0.00, 0.00, 0.00,   0.05, 0.00,   0.00, 0.65,  0.10, 0.10;
    
    A[7] << 0.10, 0.10, 0.10,   0.00, 0.00,   0.00, 0.05,  0.55, 0.10;
    A[8] << 0.10, 0.10, 0.10,   0.00, 0.00,   0.05, 0.00,  0.10, 0.45;
    
    
    HiddenMarkovModel * model = new HiddenMarkovModel(A);
    
    
    model->addModelForState(getDefaultModelForState(high_light, high_light_stddev, no_motion, high_wave,sc_high, sc_high_stddev, no_penalty));
    model->addModelForState(getDefaultModelForState(high_light,  high_light_stddev,  no_motion, low_wave,sc_high, sc_high_stddev, no_penalty));
     model->addModelForState(getDefaultModelForState(low_light,  low_light_stddev,  no_motion, low_wave,sc_low, sc_low_stddev, no_penalty));
    
    model->addModelForState(getDefaultModelForState(high_light, high_light_stddev, high_motion, high_wave, sc_high,  sc_high_stddev,  no_penalty));
    model->addModelForState(getDefaultModelForState(low_light,  low_light_stddev,  high_motion, high_wave, sc_high,  sc_high_stddev,  no_penalty));
    
    model->addModelForState(getDefaultModelForState(low_light,  low_light_stddev,   low_motion, vlow_wave, sc_low,  sc_low_stddev,  no_penalty));
    model->addModelForState(getDefaultModelForState(high_light, high_light_stddev,  low_motion, vlow_wave, sc_low,  sc_low_stddev,  yes_penalty));
    
    model->addModelForState(getDefaultModelForState(high_light,  high_light_stddev, high_motion, high_wave, sc_high,  sc_high_stddev,  no_penalty));
    model->addModelForState(getDefaultModelForState(low_light,   low_light_stddev,  high_motion, high_wave, sc_high,  sc_high_stddev,  no_penalty));
    
    
    return model;
}


HiddenMarkovModel * HmmFactory::getModel(const std::string & modelname) {
    if (modelname == "default") {
        std::cout << "found default model" << std::endl;
        return getDefaultModel();
    }
    else if (modelname == "test") {
        std::cout << "found test model" << std::endl;
        return getTestModel();
    }
    else if (modelname == "seed") {
        std::cout << "found seed model" << std::endl;
        return getSingleStateModel();
    }
    

    return NULL;

}
