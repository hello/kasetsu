

#include "trainer.h"
#include <iostream>



bool Trainer::train (HiddenMarkovModel * hmm, const HmmDataMatrix_t & meas,const int maxiter) {
    HmmFloat_t cost;

    hmm->InitializeReestimation(meas);
    
    cost = hmm->getModelCost(meas);
    std::cout << cost << std::endl;

    
    for (int iter = 0; iter < maxiter; iter++) {
        //ReestimationResult_t res = hmm->reestimate(meas);
        hmm->reestimateViterbi(meas);
        //cost = res.getLogLikelihood();
        //std::cout << cost << std::endl;
        
        
    }
    
    
    return true;
    
}

bool Trainer::grow (HiddenMarkovModel * hmm,const HmmDataMatrix_t & meas,const int maxiter) {
   
    HiddenMarkovModel * enlarged = hmm->enlargeWithVSTACS(meas,5);
    
    int foo = 3;
    foo++;
    
    return true;
}


