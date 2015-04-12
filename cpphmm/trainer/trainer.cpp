

#include "trainer.h"

#define MAX_ITER (50)
#define MIN_PERCENTAGE_CHANGE (0.001)
#define MAX_CONVERGE_COUNT (3)

bool Trainer::train (HiddenMarkovModel * hmm, const HmmDataMatrix_t & meas) {
    ReestimationResult_t lastResult;
    int convergeCount = 0;
    bool converged = false;
    
    for (int iter = 0; iter < MAX_ITER; iter++) {
        const ReestimationResult_t result =  hmm->reestimate(meas);
        
        if (lastResult.isValid() && result.isValid()) {
            const HmmFloat_t dy = lastResult.getLogLikelihood() - result.getLogLikelihood();
            const HmmFloat_t avg = 0.5 * (lastResult.getLogLikelihood() + result.getLogLikelihood());
            const HmmFloat_t percentageChange = dy / avg;
            
            if (percentageChange > 0 && percentageChange < MIN_PERCENTAGE_CHANGE) {
                convergeCount++;
            }
            else {
                convergeCount = 0;
            }
            
            if (convergeCount > MAX_CONVERGE_COUNT) {
                converged = true;
                break;
            }
        }
        
        
        lastResult = result;
        
    }
    
    
    return converged;
    
}

