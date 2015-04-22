

#include "trainer.h"
#include <iostream>

#define MAX_ITER (30)
#define MIN_PERCENTAGE_CHANGE (0.001)
#define MAX_CONVERGE_COUNT (20)

bool Trainer::train (HiddenMarkovModel * hmm, const HmmDataMatrix_t & meas,const int maxiter) {
    ReestimationResult_t lastResult;
    int convergeCount = 0;
    bool converged = false;
    
    for (int iter = 0; iter < maxiter; iter++) {
        const ReestimationResult_t result =  hmm->reestimate(meas);
        
        std::cout << result.getLogLikelihood() << std::endl;
        
        if (lastResult.isValid() && result.isValid()) {
            const HmmFloat_t dy = result.getLogLikelihood() - lastResult.getLogLikelihood();
            const HmmFloat_t avg = 0.5 * (lastResult.getLogLikelihood() + result.getLogLikelihood());
            const HmmFloat_t percentageChange = dy / avg;
            
            if (percentageChange > -MIN_PERCENTAGE_CHANGE) {
                convergeCount++;
            }
            
            if (convergeCount >= MAX_CONVERGE_COUNT) {
                converged = true;
                break;
            }
        }
        
        
        lastResult = result;
        
    }
    
    
    return converged;
    
}

