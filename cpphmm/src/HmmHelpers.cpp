#include "HmmHelpers.h"
#include "LogMath.h"
#include "MatrixHelpers.h"
#include <assert.h>

static HmmDataMatrix_t getLogAWithForbiddenStates(const HmmDataMatrix_t & logA,const TransitionMultiMap_t & forbiddenTransitions, uint32_t t) {
    
    HmmDataMatrix_t logA2 = logA;
    
    auto itpair =  forbiddenTransitions.equal_range(t);
    
    for (auto it = itpair.first; it != itpair.second; it++) {
        const uint32_t i1 = (*it).second.from;
        const uint32_t i2 = (*it).second.to;
        
        logA2[i1][i2] = LOGZERO;
    }
    
    return logA2;
    
}

static bool getLabel(uint32_t & label, const uint32_t t, const LabelMap_t & labels) {
    auto it = labels.find(t);
    
    if (it == labels.end()) {
        return false;
    }
    
    label = (*it).second;
    
    return true;
}

AlphaBetaResult_t HmmHelpers::getAlphaAndBeta(int32_t numObs,const HmmDataVec_t & pi, const HmmDataMatrix_t & logbmap, const HmmDataMatrix_t & A,const uint32_t numStates,const LabelMap_t & labels, const TransitionMultiMap_t & forbiddenTransitions) {
    
    /*
     Calculates 'alpha' the forward variable.
     
     The alpha variable is a numpy array indexed by time, then state (NxT).
     alpha[i][t] = the probability of being in state 'i' after observing the
     first t symbols.
     
     forbidden transitions means at that time index a transition is unavailable
     labels mean that you have to be in that time
     */
    int t,j,i;
    HmmDataMatrix_t logalpha = getLogZeroedMatrix(numStates,numObs);
    HmmDataMatrix_t logbeta = getLogZeroedMatrix(numStates,numObs);
    HmmFloat_t temp;
    HmmDataMatrix_t logA = A; //copy
    
    //nominal A matrix
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
        
        HmmDataMatrix_t logAThisTimeStep = getLogAWithForbiddenStates(logA,forbiddenTransitions,t);
        
        for (j = 0; j < numStates; j++) {
            temp = LOGZERO;
            
            for (i = 0; i < numStates; i++) {
                //alpha[j][t] += alpha[i][t-1]*A[i][j];
                const HmmFloat_t tempval = elnproduct(logalpha[i][t-1],logAThisTimeStep[i][j]);
                temp = elnsum(temp,tempval);
            }
            
            //alpha[j][t] *= bmap[j][t];
            logalpha[j][t] = elnproduct(temp, logbmap[j][t]);
        }
        
        uint32_t label;
        if (getLabel(label,t,labels)) {
            logalpha[label][t] = LOGZERO;
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
        
        HmmDataMatrix_t logAThisTimeStep = getLogAWithForbiddenStates(logA,forbiddenTransitions,t);

        for (i = 0; i < numStates; i++) {
            temp = LOGZERO;
            for (j = 0;  j < numStates; j++) {
                const HmmFloat_t tempval  = elnproduct(logbmap[j][t+1], logbeta[j][t+1]);
                const HmmFloat_t tempval2 = elnproduct(tempval, logAThisTimeStep[i][j]);
                temp = elnsum(temp,tempval2);
                //beta[i][t] += A[i][j]*bmap[j][t+1] * beta[j][t+1];
            }
            
            logbeta[i][t] = temp;
        }
        
        uint32_t label;
        if (getLabel(label,t,labels)) {
            logbeta[label][t] = LOGZERO;
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

Hmm3DMatrix_t HmmHelpers::getLogXi(const AlphaBetaResult_t & alphabeta,const HmmDataMatrix_t & logbmap, const uint32_t numObs,const uint32_t numStates) {

    TransitionMultiMap_t forbiddenTransitions;

    return getLogXi(alphabeta, logbmap, forbiddenTransitions, numObs,numStates);
}

Hmm3DMatrix_t HmmHelpers::getLogXi(const AlphaBetaResult_t & alphabeta,const HmmDataMatrix_t & logbmap,const TransitionMultiMap_t & forbiddenTransitions, const uint32_t numObs,const uint32_t numStates) {
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
        
        HmmDataMatrix_t logAThisTimeStep = getLogAWithForbiddenStates(logA,forbiddenTransitions,t);

        for (i = 0; i < numStates; i++) {
            for (j = 0; j < numStates; j++) {
                
                const HmmFloat_t tempval1 = elnproduct(logalpha[i][t], logAThisTimeStep[i][j]);
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

HmmDataMatrix_t HmmHelpers::getLogGamma(const AlphaBetaResult_t & alphabeta,uint32_t numObs, uint32_t numStates) {
    /*
     Calculates 'gamma' from xi.
     
     Gamma is a (TxN) numpy array, where gamma[t][i] = the probability of being
     in state 'i' at time 't' given the full observation sequence.
     */
    
    int32_t t,i;
    HmmFloat_t normalizer;
    HmmFloat_t temp;
    HmmDataMatrix_t loggamma = getLogZeroedMatrix(numStates, numObs);
    
    for (t = 0; t < numObs; t++) {
        normalizer = LOGZERO;
        for (i = 0; i < numStates; i++) {
            temp = elnproduct(alphabeta.logalpha[i][t], alphabeta.logbeta[i][t]);
            loggamma[i][t] = temp;
            normalizer = elnsum(normalizer, temp);
        }
        
        
        for (i = 0; i < numStates; i++) {
            loggamma[i][t] = elnproduct(loggamma[i][t], -normalizer);
        }
    }
    
    return loggamma;
    
}

HmmDataMatrix_t HmmHelpers::reestimateA(const HmmDataMatrix_t & A, const Hmm3DMatrix_t & logxi, const HmmDataMatrix_t & loggamma,const size_t numObs,const HmmFloat_t damping, const HmmFloat_t minValueForA, const uint32_t numStates) {
    
    int32_t i,j,t;
    HmmDataMatrix_t A2 = getZeroedMatrix(numStates, numStates);
    
    for (i = 0; i < numStates; i++) {
        HmmFloat_t denom = LOGZERO;
        
        for (t = 0; t < numObs; t++) {
            denom = elnsum(denom, loggamma[i][t]) ;
        }
        
        for (j = 0; j < numStates; j++) {
            HmmFloat_t numer = LOGZERO;
            for (t = 0; t < numObs; t++) {
                numer = elnsum(numer,logxi[i][j][t]);
            }
            
            A2[i][j] = eexp(elnproduct(numer, -denom));
            
            if (A[i][j] > EPSILON) {
                if (A2[i][j] <= minValueForA) {
                    A2[i][j] = minValueForA;
                }
            }
        }
    }
    
    
    for (j = 0; j < numStates; j++) {
        for (i = 0; i < numStates; i++) {
            A2[j][i] = damping * A2[j][i] + (1.0 - damping) * A[j][i];
        }
    }
    
    for (j = 0; j < numStates; j++) {
        HmmFloat_t sum = 0.0;
        for (i = 0; i < numStates; i++) {
            sum += A2[j][i];
        }
        
        if (sum < EPSILON) {
            continue;
        }
        
        for (i = 0; i < numStates; i++) {
            A2[j][i] /= sum;
        }
    }
    
    for (j = 0; j < numStates; j++) {
        for (i = 0; i < numStates; i++) {
            
            if (A2[j][i] > EPSILON) {
                if (A2[j][i] <= minValueForA) {
                    A2[j][i] = minValueForA;
                }
                
                if (A2[j][i] > minValueForA) {
                    A2[j][i] = minValueForA;
                }
            }
            
        }
    }
    
    return A;
    
}


HmmDataMatrix_t HmmHelpers::getLogANumerator(const AlphaBetaResult_t & alphabeta,const HmmDataMatrix_t & logbmap,const TransitionMultiMap_t & forbiddenTransitions,const size_t numObs, const uint32_t numStates) {
    
    int32_t i,j,t;
    HmmDataMatrix_t logANumerator = getLogZeroedMatrix(numStates, numStates);
    
    const HmmDataMatrix_t & logalpha = alphabeta.logalpha;
    const HmmDataMatrix_t & logbeta = alphabeta.logbeta;
    const HmmDataMatrix_t & logA = alphabeta.logA;
    
    
    for (i = 0; i < numStates; i++) {
        for (j = 0; j < numStates; j++) {
            HmmFloat_t numer = LOGZERO;
            
            for (t = 0; t < numObs - 1; t++) {
                HmmDataMatrix_t logAThisTimeStep = getLogAWithForbiddenStates(logA,forbiddenTransitions,t);
                
                const HmmFloat_t tempval1 = elnproduct(logalpha[i][t], logAThisTimeStep[i][j]);
                const HmmFloat_t tempval2 = elnproduct(logbmap[j][t+1], logbeta[j][t+1]);
                const HmmFloat_t tempval3 = elnproduct(tempval1,tempval2);
                
                numer = elnsum(numer,tempval3);
            }
            
            logANumerator[i][j] = numer;
        }
    }
    
    
    
    for (i = 0; i < numStates; i++) {
        for (j = 0; j < numStates; j++) {
            logANumerator[j][i] = elnproduct(logANumerator[j][i], -alphabeta.logmodelcost);
        }
    }
    
    
    return logANumerator;
    
}

HmmDataMatrix_t HmmHelpers::getLogAlphabetNumerator(const AlphaBetaResult_t & alphabeta, const HmmDataVec_t & rawdata, const uint32_t numStates, const uint32_t numObs, const uint32_t alphabetSize ) {
    
    int32_t iState,iAlphabet,t;

    HmmDataMatrix_t logAlphabetNumerator = getLogZeroedMatrix(numStates, alphabetSize);

    const HmmDataMatrix_t & logalpha = alphabeta.logalpha;
    const HmmDataMatrix_t & logbeta = alphabeta.logbeta;
    
    for (iState = 0; iState < numStates; iState++) {
       
        for (t = 0; t < numObs; t++) {
            const uint32_t idx = (uint32_t)rawdata[t];
            
            assert(idx >= 0 && idx < alphabetSize);
            
            logAlphabetNumerator[iState][idx] = elnsum(logAlphabetNumerator[iState][idx] ,elnproduct(logalpha[iState][t], logbeta[iState][t]));
        }

    }

    
    for (iState = 0; iState < numStates; iState++) {
        for (iAlphabet = 0; iAlphabet < alphabetSize; iAlphabet++) {
            logAlphabetNumerator[iState][iAlphabet] = elnproduct(logAlphabetNumerator[iState][iAlphabet], -alphabeta.logmodelcost);
        }
    }
    
    return logAlphabetNumerator;


}


HmmDataVec_t HmmHelpers::getLogDenominator(const AlphaBetaResult_t & alphabeta, const uint32_t numStates, const uint32_t numObs) {
    
    int32_t iState,t;
    
    HmmDataVec_t logDenominator = getLogZeroedVec(numStates);
    
    const HmmDataMatrix_t & logalpha = alphabeta.logalpha;
    const HmmDataMatrix_t & logbeta = alphabeta.logbeta;
    
    for (iState = 0; iState < numStates; iState++) {
        for (t = 0; t < numObs; t++) {
            logDenominator[iState] = elnsum(logDenominator[iState],elnproduct(logalpha[iState][t], logbeta[iState][t]));
        }
        
        logDenominator[iState] = elnproduct(logDenominator[iState], -alphabeta.logmodelcost);
    }
    
    return logDenominator;
}

HmmDataMatrix_t HmmHelpers::elnAddMatrix(const HmmDataMatrix_t & m1, const HmmDataMatrix_t & m2) {
    const int m = m1.size();
    const int n = m1[0].size();
    
    HmmDataMatrix_t m3 = getZeroedMatrix(m, n);
    
    for (int j = 0; j < m; j++) {
        for (int i = 0; i < n; i++) {
            m3[j][i] = elnsum(m1[j][i], m2[j][i]);
        }
    }
    
    return m3;
}

HmmDataVec_t HmmHelpers::elnAddVector(const HmmDataVec_t & m1, const HmmDataVec_t & m2) {
    const int m = m1.size();
    
    HmmDataVec_t m3 = getZeroedVec(m);
    
    for (int j = 0; j < m; j++) {
        m3[j] = elnsum(m1[j], m2[j]);
        
    }
    
    return m3;
}


