#include "hmmfactory.h"
#include <string>
#include "CompositeModel.h"
#include "AllModels.h"

static HmmPdfInterface * getDefaultModelForState(float lightGammaMean, float lightGammStdDev, float movementPoissonMean, float disturbanceFraction, float soundcountGammaMean, float soundcountGammaStdDev, float natlightPenaltyFraction) {
    
    
    HmmDataVec_t disturbanceProbs;
    disturbanceProbs.resize(2);
    disturbanceProbs[0] = 1.0 - disturbanceFraction;
    disturbanceProbs[1] = disturbanceFraction;
    
    HmmDataVec_t natlightProbs;
    natlightProbs.resize(2);
    natlightProbs[0] = 1.0 - natlightPenaltyFraction;
    natlightProbs[1] = natlightPenaltyFraction;
    
    CompositeModel * p = new CompositeModel();
    
    p->addModel(new GammaModel(0,lightGammaMean,lightGammStdDev));
    p->addModel(new PoissonModel(1,movementPoissonMean));
    p->addModel(new AlphabetModel(2,disturbanceProbs,true));
    p->addModel(new GammaModel(3,lightGammaMean,lightGammStdDev));
    p->addModel(new AlphabetModel(4,natlightProbs,false));
    
    return p;

}


static HiddenMarkovModel * getDefaultModel() {
    const int num_states = 11;
    
    HmmDataMatrix_t A;
    
    A.resize(num_states);
    
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
    A[10] << 0.10, 0.10, 0.10, 0.10,   0.00, 0.00,    0.05, 0.05, 0.00,   0.10, 0.45;

    
    
    HiddenMarkovModel * model = new HiddenMarkovModel(A);
    
  //  model->addModelForState(getDefaultModelForState()
    
    return model;
}


HiddenMarkovModel * HmmFactory::getModel(const std::string & modelname) {
    if (modelname == "default") {
        return getDefaultModel();
    }
    

    return NULL;

}
