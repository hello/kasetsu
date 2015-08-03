#include "HmmHelpers.h"
#include "LogMath.h"
#include "MatrixHelpers.h"

AlphaBetaResult_t HmmHelpers::getAlphaAndBeta(int32_t numObs,const HmmDataVec_t & pi, const HmmDataMatrix_t & logbmap, const HmmDataMatrix_t & A,const uint32_t numStates,const LabelMap_t & labels, const TransitionMultiMap_t & forbiddenTransitions) {
    
    /*
     Calculates 'alpha' the forward variable.
     
     The alpha variable is a numpy array indexed by time, then state (NxT).
     alpha[i][t] = the probability of being in state 'i' after observing the
     first t symbols.
     */
    int t,j,i;
    HmmDataMatrix_t logalpha = getLogZeroedMatrix(numStates,numObs);
    HmmDataMatrix_t logbeta = getLogZeroedMatrix(numStates,numObs);
    HmmFloat_t temp;
    HmmDataMatrix_t logA = A; //copy
    
    for (j = 0; j < numStates; j++) {
        for (i = 0; i < numStates; i++) {
            logA[j][i] = eln(logA[j][i]);
        }
    }
    
    
    //init stage - alpha_1(x) = pi(x)b_x(O1)
    
    for (j = 0; j < numStates; j++) {
        logalpha[j][0] = elnproduct(eln(pi[j]), logbmap[j][0]);
    }
    
    
    for (t = 1; t < numObs; t++) {
        for (j = 0; j < numStates; j++) {
            temp = LOGZERO;
            
            for (i = 0; i < numStates; i++) {
                const HmmFloat_t tempval = elnproduct(logalpha[i][t-1],logA[i][j]);
                temp = elnsum(temp,tempval);
                //alpha[j][t] += alpha[i][t-1]*A[i][j];
            }
            
            if (temp == LOGZERO) {
                int foo = 3;
                foo++;
            }
            
            logalpha[j][t] = elnproduct(temp, logbmap[j][t]);
            //alpha[j][t] *= bmap[j][t];
        }
        
    }
    
    /*
     Calculates 'beta' the backward variable.
     
     The beta variable is a numpy array indexed by time, then state (NxT).
     beta[i][t] = the probability of being in state 'i' and then observing the
     symbols from t+1 to the end (T).
     */
    
    
    // init stage
    for (int s = 0; s < numStates; s++) {
        logbeta[s][numObs - 1] = 0.0;
    }
    
    
    
    for (t = numObs - 2; t >= 0; t--) {
        for (i = 0; i < numStates; i++) {
            temp = LOGZERO;
            for (j = 0;  j < numStates; j++) {
                const HmmFloat_t tempval  = elnproduct(logbmap[j][t+1], logbeta[j][t+1]);
                const HmmFloat_t tempval2 = elnproduct(tempval, logA[i][j]);
                temp = elnsum(temp,tempval2);
                //beta[i][t] += A[i][j]*bmap[j][t+1] * beta[j][t+1];
            }
            
            logbeta[i][t] = temp;
            
        }
    }
    
    temp = LOGZERO;
    for (i = 0; i < numStates; i++) {
        temp = elnsum(temp,logalpha[i][numObs-1]);
    }
    
    
    const AlphaBetaResult_t result(logalpha,logbeta,logA,temp);
    
    return result;
    

    
}

AlphaBetaResult_t HmmHelpers::getAlphaAndBeta(int32_t numObs,const HmmDataVec_t & pi, const HmmDataMatrix_t & logbmap, const HmmDataMatrix_t & A, const uint32_t numStates) {
    
    //pass empty structures
    LabelMap_t labels;
    TransitionMultiMap_t forbiddenTransitions;
    
    return getAlphaAndBeta(numObs, pi, logbmap, A, numStates, labels, forbiddenTransitions);
    
}


Hmm3DMatrix_t HmmHelpers::getLogXi(const AlphaBetaResult_t & alphabeta,const HmmDataMatrix_t & logbmap,const uint32_t numObs,const uint32_t numStates) {
    /*
     Calculates 'xi', a joint probability from the 'alpha' and 'beta' variables.
     
     The xi variable is a numpy array indexed by time, state, and state (TxNxN).
     xi[t][i][j] = the probability of being in state 'i' at time 't', and 'j' at
     time 't+1' given the entire observation sequence.
     */
    int32_t t,i,j;
    
    const HmmDataMatrix_t & logalpha = alphabeta.logalpha;
    const HmmDataMatrix_t & logbeta = alphabeta.logbeta;
    const HmmDataMatrix_t & logA = alphabeta.logA;
    Hmm3DMatrix_t logxi = getLogZeroed3dMatrix(numStates,numStates, numObs);
    HmmDataVec_t tempvec = getZeroedVec(numStates);
    HmmDataVec_t logdenomvec = getZeroedVec(numStates);
    HmmFloat_t normalizer;
    
    for (t = 0; t < numObs - 1; t++) {
        normalizer = LOGZERO;
        
        for (i = 0; i < numStates; i++) {
            for (j = 0; j < numStates; j++) {
                
                const HmmFloat_t tempval1 = elnproduct(logalpha[i][t], logA[i][j]);
                const HmmFloat_t tempval2 = elnproduct(logbmap[j][t+1], logbeta[j][t+1]);
                const HmmFloat_t tempval3 = elnproduct(tempval1,tempval2);
                
                logxi[i][j][t] = tempval3;
                
                normalizer = elnsum(tempval3, normalizer);
            }
        }
        
        
        for (i = 0; i < numStates; i++) {
            for (j = 0; j < numStates; j++) {
                logxi[i][j][t] = elnproduct(logxi[i][j][t], -normalizer);
            }
            
        }
        
    }
    
    return logxi;
    
}



HmmDataMatrix_t HmmHelpers::getLogBMap(const ModelVec_t & models, const HmmDataMatrix_t & meas) {
    HmmDataMatrix_t logbmap;
    
    
    for (ModelVec_t::const_iterator it = models.begin(); it != models.end(); it++) {
        const HmmPdfInterface * ref = (*it).get();
        logbmap.push_back(ref->getLogOfPdf(meas));
    }
    
    return logbmap;
}


