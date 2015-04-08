#include "HiddenMarkovModel.h"
#include "HmmTypes.h"
#include <math.h>

#define MIN_NORMALIZING_VALUE (1e-3)
#define MIN_LOG_BMAP (-15.0)

HiddenMarkovModel::HiddenMarkovModel(int32_t numStates)
: _numStates(numStates) {
    
}

HiddenMarkovModel::~HiddenMarkovModel() {
    
}

void HiddenMarkovModel::addModelForState(int32_t stateNum, HmmPdfInterface * model) {
    
}


static HmmDataMatrix_t getNormalizedBMap(const HmmDataMatrix_t & logbmap, HmmFloat_t & maximum) {
    //normalize logbamp
    HmmDataMatrix_t bmap = logbmap; //should copy everything
    const size_t numStates = logbmap.size();
    
    maximum = -INFINITY;
    for (int j = 0; j < numStates; j++) {
        HmmDataVec_t & brow = bmap[j];
        for (int i = 0; i < brow.size(); i++) {
            HmmFloat_t val = brow[i];
            
            if (val > maximum) {
                maximum = val;
            }
        }
    }
    
    for (int j = 0; j < numStates; j++) {
        HmmDataVec_t & brow = bmap[j];
        for (int i = 0; i < brow.size(); i++) {
            brow[i] -= maximum;
            
            if (brow[i] < MIN_LOG_BMAP) {
                brow[i] = MIN_LOG_BMAP;
            }
            
            brow[i] = exp(brow[i]);
        }
    }
    
    return bmap;

}

static HmmDataVec_t getZeroedVec(size_t vecSize) {
    HmmDataVec_t vec;
    vec.resize(vecSize);
    memset(vec.data(),0,sizeof(HmmFloat_t) * vecSize);
    return vec;
}

static HmmDataMatrix_t getZeroedMatrix(size_t numVecs, size_t vecSize) {
    HmmDataMatrix_t mtx;
    mtx.resize(numVecs);
    
    //allocate and zero out
    for(int j = 0; j < numVecs; j++) {
        mtx[j] = getZeroedVec(vecSize);
    }
    
    return mtx;
}


AlphaBetaResult_t HiddenMarkovModel::getAlphaAndBeta(int32_t numObs,const HmmDataVec_t & pi, const HmmDataMatrix_t & logbmap, const HmmDataMatrix_t A) const {
    /*
    Calculates 'alpha' the forward variable.
    
    The alpha variable is a numpy array indexed by time, then state (NxT).
    alpha[i][t] = the probability of being in state 'i' after observing the
    first t symbols.
    */
    int t,j,i;
    HmmDataMatrix_t alpha = getZeroedMatrix(_numStates,numObs);
    HmmDataMatrix_t beta = getZeroedMatrix(_numStates,numObs);

    HmmFloat_t logmaximum = 0;
    HmmDataMatrix_t bmap = getNormalizedBMap(logbmap,logmaximum);
    
    HmmDataVec_t c = getZeroedVec(numObs);
    c[0] = 1.0;
    
    //init stage - alpha_1(x) = pi(x)b_x(O1)

    for (j = 0; j < _numStates; j++) {
        alpha[j][0] = pi[j]*bmap[j][0];
    }
    
    
    for (t = 1; t < numObs; t++) {
        for (j = 0; j < _numStates; j++) {
            for (i = 0; i < _numStates; i++) {
                alpha[j][t] += alpha[j][t-1]*A[i][j];
            }
            
            alpha[j][t] *= bmap[j][t];
            c[t] += alpha[j][t];
        }
        
        if (c[t] < MIN_NORMALIZING_VALUE) {
            c[t] = MIN_NORMALIZING_VALUE;
        }
        
        for (int j = 0; j < _numStates; j++) {
            alpha[j][t] /= c[t];
        }
    }
    
    /*
        Calculates 'beta' the backward variable.
                        
        The beta variable is a numpy array indexed by time, then state (NxT).
        beta[i][t] = the probability of being in state 'i' and then observing the
        symbols from t+1 to the end (T).
     */
    
                        
    // init stage
    for (int s = 0; s < _numStates; s++) {
        beta[s][numObs - 1] = 1.0;
    }
    
    for (t = numObs - 2; t >= 0; t--) {
        for (i = 0; i < _numStates; i++) {
            for (j = 0;  j< _numStates; j++) {
                beta[i][t] += A[i][j]*bmap[t+1][j] * beta[j][t+1];
            }
            
            for (j = 0; j < _numStates; j++) {
                beta[j][t] /= c[t];
            }
        }
    }
    
    HmmFloat_t sumc = 0.0;
    for (t = 0; t < numObs; t++) {
        sumc += log(c[t]);
    }
    
    sumc += logmaximum * numObs;
    
    const AlphaBetaResult_t result(alpha,beta,sumc);
    
    return result;
    
    

}

void HiddenMarkovModel::reestimate() {
    
}