

#include "trainer.h"
#include <iostream>



bool Trainer::train (HiddenMarkovModel * hmm, const HmmDataMatrix_t & meas,const int maxiter) {
    HmmFloat_t cost;
    ReestimationResult_t res;
    
    res = hmm->reestimateViterbi(meas);
    res = hmm->reestimateViterbi(meas);

    cost = hmm->getModelCost(meas);
    std::cout << cost << std::endl;

    
    for (int iter = 0; iter < maxiter; iter++) {
        res = hmm->reestimate(meas);
        //res = hmm->reestimateViterbi(meas);
        cost = res.getLogLikelihood();
        std::cout << cost << std::endl;
        
    }
    
    //res = hmm->reestimate(meas);
    //cost = res.getLogLikelihood();

    std::cout << cost << std::endl;

    
    
    return true;
    
}

bool Trainer::grow (HiddenMarkovModel * hmm,const HmmDataMatrix_t & meas,const int maxiter) {

    //hmm->enlargeRandomly(meas,maxiter);
    hmm->enlargeWithVSTACS(meas, maxiter);
    //hmm->enlargeWithIndirectSplits(meas, maxiter);
    return true;
}


