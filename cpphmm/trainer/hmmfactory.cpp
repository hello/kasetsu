#include "hmmfactory.h"
#include <string>
#include "CompositeModel.h"
#include "AllModels.h"
#include <iostream>
#include "InitialModelGenerator.h"
#include "json/json.h"

static HmmSharedPtr_t loadFile(const std::string jsonText) {
    Json::Value top;
    Json::Reader reader;
    if (!reader.parse(jsonText, top)) {
        return HmmSharedPtr_t(NULL);
    }
    
    
    
    Json::Value::Members members = top.getMemberNames();
    
    for (Json::Value::Members::const_iterator it = members.begin(); it != members.end(); it++) {
        
    }
    
    return HmmSharedPtr_t(NULL);

}


static HmmFloat_t getRandomPositiveFloat() {
    const float r = 1.0 * static_cast <HmmFloat_t> (rand()) / static_cast <HmmFloat_t> (RAND_MAX);
    return r;
}

static HmmDataMatrix_t getRandomMatrix(int m, int n) {
    HmmDataMatrix_t  A;
    A.resize(m);
    
    for (int j = 0; j < m; j++) {
        for (int i = 0; i < n; i++) {
            A[j].push_back(getRandomPositiveFloat());
        }
        
        HmmFloat_t sum = 0.0;
        for (int i = 0; i < n; i++) {
            sum += A[j][i];
        }
    
        
        for (int i = 0; i < n; i++) {
            A[j][i] /= sum;
        }
    }
    
    return A;
    
}



static HmmPdfInterfaceSharedPtr_t getDefaultModelForState(float lightGammaMean, float lightGammStdDev, float movementPoissonMean, float disturbanceFraction, float soundcountGammaMean, float soundcountGammaStdDev, float natlightPenaltyFraction,bool useNatLight = true, bool estimateNatLight = false) {
    
    
    HmmDataVec_t disturbanceProbs;
    disturbanceProbs.resize(2);
    disturbanceProbs[0] = 1.0 - disturbanceFraction;
    disturbanceProbs[1] = disturbanceFraction;
    
    HmmDataVec_t natlightProbs;
    natlightProbs.resize(2);
    natlightProbs[0] = 1.0;
    natlightProbs[1] = natlightPenaltyFraction;
    
    CompositeModel * p = new CompositeModel();
    
    p->addModel(HmmPdfInterfaceSharedPtr_t(new GammaModel(0,lightGammaMean,lightGammStdDev,1.0)));
    p->addModel(HmmPdfInterfaceSharedPtr_t(new PoissonModel(1,movementPoissonMean,1.0)));
    p->addModel(HmmPdfInterfaceSharedPtr_t(new AlphabetModel(2,disturbanceProbs,true,1.0)));
    p->addModel(HmmPdfInterfaceSharedPtr_t(new GammaModel(3,lightGammaMean,lightGammStdDev,1.0)));
    
    if (useNatLight)  {
        p->addModel(HmmPdfInterfaceSharedPtr_t(new AlphabetModel(4,natlightProbs,estimateNatLight,1.0)));
    }
    
    return HmmPdfInterfaceSharedPtr_t(p);

}

static HiddenMarkovModel * getSingleStateModel() {
    const int num_states = 1;

    HmmDataMatrix_t A;
    
    A.resize(num_states);
    A[0] << 1.0;

    HiddenMarkovModel * model = new HiddenMarkovModel(A);

    model->addModelForState(getDefaultModelForState(1.0, 1.0, 1.0, 0.5,1.0, 1.0, 1.0,false,false));
    
    return model;

}


static HiddenMarkovModel * getSeedModel(const HmmDataMatrix_t & meas,SaveStateInterface * stateSaver,EInitModel_t model) {
    InitialModel_t modelparams = InitialModelGenerator::getInitialModelFromData(meas,model);
    
    HiddenMarkovModel * newmodel = new HiddenMarkovModel(modelparams.A,stateSaver);
    
    for (int i = 0; i < modelparams.models.size(); i++) {
        newmodel->addModelForState(modelparams.models[i]);
    }
    
    return newmodel;
    
}



static HiddenMarkovModel * getRandomModel() {
    const int N = 3;
    
    const bool useNatLight = false;
    const bool estimateNatLight = false;
    
    
    UIntVec_t groups;
    for (int i = 0; i < N; i++) {
        groups.push_back(i);
    }
    
    HiddenMarkovModel * model = new HiddenMarkovModel(getRandomMatrix(N,N),NULL);
    
    for (int i = 0; i < N; i++) {
        model->addModelForState(getDefaultModelForState(
                                                        getRandomPositiveFloat() * 5, 1.0,
                                                        getRandomPositiveFloat() * 5,
                                                        getRandomPositiveFloat(),
                                                        getRandomPositiveFloat() * 5, 1.0,
                                                        1.0,useNatLight,estimateNatLight));
    }
    
    return model;
    
}

static HiddenMarkovModel * getRandomSparseModel() {
    const int N = 20;
    const float sparseThreshold = 0.1 / N;
    
    const bool useNatLight = false;
    const bool estimateNatLight = false;
    
    
    UIntVec_t groups;
    for (int i = 0; i < N; i++) {
        groups.push_back(i);
    }
    
    HmmDataMatrix_t A = getRandomMatrix(N,N);
    
    for (int j = 0; j < N; j++) {
        for (int i = 0; i < N; i++) {
            if (A[j][i] < sparseThreshold) {
                A[j][i] = 0;
            }
        }
    }
    
    
    
    HiddenMarkovModel * model = new HiddenMarkovModel(A);
    
    for (int i = 0; i < N; i++) {
        model->addModelForState(getDefaultModelForState(
                                                        getRandomPositiveFloat() * 5, 1.0,
                                                        getRandomPositiveFloat() * 5,
                                                        getRandomPositiveFloat(),
                                                        getRandomPositiveFloat() * 5, 1.0,
                                                        1.0,useNatLight,estimateNatLight));
    }
    
    return model;
    
}

static HiddenMarkovModel * getDefaultModel() {
    const int num_states = 12;
    
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
    
    const float sc_low = 0.3;
    const float sc_high = 2.0;
    const float sc_low_stddev = 0.5;
    const float sc_high_stddev = 1.0;
    
    const float no_penalty = 1.0;
    const float yes_penalty = 1e-6;
    
    
    A[0] << 0.65, 0.10, 0.10, 0.10,   0.10,  0.10,   0.00, 0.00, 0.00,   0.00, 0.00, 0.01;
    A[1] << 0.10, 0.65, 0.10, 0.10,   0.10,  0.10,   0.00, 0.00, 0.00,   0.00, 0.00, 0.01;
    A[2] << 0.10, 0.10, 0.65, 0.10,   0.10,  0.10,   0.00, 0.00, 0.00,   0.00, 0.00, 0.01;
    A[3] << 0.10, 0.10, 0.10, 0.65,   0.10,  0.10,   0.00, 0.00, 0.00,   0.00, 0.00, 0.01;
    
    A[4] << 0.05, 0.05, 0.05, 0.05,   0.70, 0.10,    0.10, 0.10, 0.00,   0.00, 0.00, 0.00;
    A[5] << 0.05, 0.05, 0.05, 0.05,   0.10, 0.70,    0.10, 0.10, 0.00,   0.00, 0.00, 0.10;
    
    A[6] << 0.00, 0.00, 0.00, 0.00,   0.00,  0.05,   0.55, 0.10, 0.05,   0.10, 0.10, 0.00;
    A[7] << 0.00, 0.00, 0.00, 0.00,   0.00,  0.05,   0.45, 0.50, 0.00,   0.00, 0.00, 0.00;
    A[8] << 0.10, 0.00, 0.10, 0.00,   0.05,  0.00,   0.00, 0.00, 0.65,   0.10, 0.10, 0.00;
    
    A[9] << 0.10, 0.10, 0.10, 0.10,   0.00, 0.00,    0.00, 0.00, 0.05,   0.55, 0.10, 0.01;
    A[10]<< 0.10, 0.10, 0.10, 0.10,   0.00, 0.00,    0.05, 0.05, 0.00,   0.10, 0.45, 0.01;
    A[11]<< 0.10, 0.10, 0.10, 0.10,   0.00, 0.00,    0.00, 0.00, 0.00,   0.00, 0.00, 0.6;


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
    model->addModelForState(getDefaultModelForState(low_light,  low_light_stddev,  no_motion, low_wave,sc_low,  sc_low_stddev,  no_penalty));


    return model;
}

static HiddenMarkovModel * getTestModel() {
    const int num_states = 11;
    bool estimateNatLight = false;
    
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
    
    
    A[0] << 0.65, 0.10, 0.10, 0.10,   0.10, 0.10,   0.00, 0.00, 0.00,   0.00, 0.00;
    A[1] << 0.10, 0.65, 0.10, 0.10,   0.10, 0.10,   0.00, 0.00, 0.00,   0.00, 0.00;
    A[2] << 0.10, 0.10, 0.65, 0.10,   0.10, 0.10,   0.00, 0.00, 0.00,   0.00, 0.00;
    A[3] << 0.10, 0.10, 0.10, 0.65,   0.10, 0.10,   0.00, 0.00, 0.00,   0.00, 0.00;

    
    A[4] << 0.05, 0.05, 0.05, 0.05,   0.70, 0.10,   0.10, 0.00, 0.00,  0.00, 0.00;
    A[5] << 0.05, 0.05, 0.05, 0.05,   0.10, 0.70,   0.10, 0.00, 0.00,  0.00, 0.00;
    
    A[6] << 0.00, 0.00, 0.00, 0.00,  0.00, 0.05,   0.55, 0.05, 0.05,  0.10, 0.10;
    A[7] << 0.00, 0.00, 0.00, 0.00,  0.05, 0.05,   0.05, 0.65, 0.00,  0.10, 0.10;
    A[8] << 0.00, 0.00, 0.00, 0.00,  0.05, 0.05,   0.05, 0.05, 0.65,  0.10, 0.10;

    A[9] << 0.10, 0.10, 0.10, 0.10,   0.00, 0.00,   0.00, 0.05, 0.00,  0.55, 0.10;
    A[10] << 0.10, 0.10, 0.10,0.10,   0.00, 0.00,   0.05, 0.00, 0.00,  0.10, 0.45;
    
    
    HiddenMarkovModel * model = new HiddenMarkovModel(A);
    
    
    model->addModelForState(getDefaultModelForState(high_light, high_light_stddev, no_motion, high_wave,sc_high, sc_high_stddev, no_penalty,true,estimateNatLight));
    model->addModelForState(getDefaultModelForState(high_light, high_light_stddev, no_motion, low_wave,sc_high, sc_high_stddev, no_penalty,true,estimateNatLight));
    model->addModelForState(getDefaultModelForState(low_light,  low_light_stddev,  no_motion, high_wave,sc_high, sc_high_stddev, no_penalty,true,estimateNatLight));
    model->addModelForState(getDefaultModelForState(low_light,  low_light_stddev,  no_motion, low_wave,sc_low, sc_low_stddev, no_penalty,true,estimateNatLight));

    model->addModelForState(getDefaultModelForState(high_light, high_light_stddev, high_motion, high_wave, sc_high,  sc_high_stddev,  no_penalty,true,estimateNatLight));
    model->addModelForState(getDefaultModelForState(low_light,  low_light_stddev,  high_motion, high_wave, sc_high,  sc_high_stddev,  no_penalty,true,estimateNatLight));
    
    model->addModelForState(getDefaultModelForState(low_light,  low_light_stddev,   low_motion, vlow_wave, sc_low,  sc_low_stddev,  no_penalty,true,estimateNatLight));
    model->addModelForState(getDefaultModelForState(low_light,  low_light_stddev,   no_motion, vlow_wave, sc_low,  sc_low_stddev,  no_penalty,true,estimateNatLight));
    model->addModelForState(getDefaultModelForState(high_light, high_light_stddev,  low_motion, vlow_wave, sc_low,  sc_low_stddev,  yes_penalty,true,estimateNatLight));
    
    model->addModelForState(getDefaultModelForState(high_light,  high_light_stddev, high_motion, high_wave, sc_high,  sc_high_stddev,  no_penalty,true,estimateNatLight));
    model->addModelForState(getDefaultModelForState(low_light,   low_light_stddev,  high_motion, high_wave, sc_high,  sc_high_stddev,  no_penalty,true,estimateNatLight));
    
    
    return model;
}


HiddenMarkovModel * HmmFactory::getModel(const std::string & modelname,const HmmDataMatrix_t & meas,SaveStateInterface * stateSaver) {
    if (modelname == "default") {
        std::cout << "found default model" << std::endl;
        return getDefaultModel();
    }
    else if (modelname == "test") {
        std::cout << "found test model" << std::endl;
        return getTestModel();
    }
    else if (modelname == "motion") {
        std::cout << "found seed model" << std::endl;
        return getSeedModel(meas,stateSaver,motion);
    }
    else if (modelname == "light") {
        std::cout << "found seed model" << std::endl;
        return getSeedModel(meas,stateSaver,light);
    }
    
  
    

    return NULL;

}
