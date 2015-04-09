#include "HiddenMarkovModel.h"
#include "HmmTypes.h"
#include <math.h>

#define MIN_NORMALIZING_VALUE (1e-3)
#define MIN_LOG_BMAP (-15.0)

HiddenMarkovModel::HiddenMarkovModel(const HmmDataMatrix_t & A)
: _numStates(_A.size())
,_A(A) {
    
}

HiddenMarkovModel::~HiddenMarkovModel() {
    
    clearModels();
    
}

void HiddenMarkovModel::clearModels() {
    for (ModelVec_t::iterator it = _models.begin(); it != _models.end(); it++) {
        delete *it;
    }
    
    _models.clear();
}

void HiddenMarkovModel::addModelForState(HmmPdfInterface * model) {
    _models.push_back(model);
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

static HmmDataVec_t getUniformVec(size_t vecSize) {
    HmmDataVec_t vec;
    HmmFloat_t a = 1.0 / (HmmFloat_t)vecSize;
    vec.resize(vecSize);
    for (int i = 0; i < vecSize; i++) {
        vec[i] = a;
    }
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

static Hmm3DMatrix_t getZeroed3dMatrix(size_t numMats, size_t numVecs, size_t vecSize) {
    Hmm3DMatrix_t mtx3;
    mtx3.reserve(numMats);
    
    for (int i = 0; i < numMats; i++) {
        mtx3.push_back(getZeroedMatrix(numVecs, vecSize));
    }
    
    return mtx3;
}

HmmDataMatrix_t HiddenMarkovModel::getLogBMap(const HmmDataMatrix_t & meas) const {
    HmmDataMatrix_t logbmap;
    
    for (ModelVec_t::const_iterator it = _models.begin(); it != _models.end(); it++) {
        const HmmPdfInterface * ref = *it;
        logbmap.push_back(ref->getLogOfPdf(meas));
    }
    
    return logbmap;
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
    
    const AlphaBetaResult_t result(alpha,beta,bmap,sumc);
    
    return result;
    
    

}

Hmm3DMatrix_t HiddenMarkovModel::getXi(const AlphaBetaResult_t & alphabeta,size_t numObs) const {
    /*
    Calculates 'xi', a joint probability from the 'alpha' and 'beta' variables.
    
    The xi variable is a numpy array indexed by time, state, and state (TxNxN).
    xi[t][i][j] = the probability of being in state 'i' at time 't', and 'j' at
    time 't+1' given the entire observation sequence.
    */
    int32_t t,i,j;

    const HmmDataMatrix_t & alpha = alphabeta.alpha;
    const HmmDataMatrix_t & beta = alphabeta.beta;
    const HmmDataMatrix_t & bmap = alphabeta.bmap;

    Hmm3DMatrix_t xi = getZeroed3dMatrix(_numStates,_numStates, numObs);
    
    
    for (t = 0; t < numObs - 1; t++) {
        HmmFloat_t denom = 0.0;
        for (i = 0; i < _numStates; i++) {
            for (j = 0; j < _numStates; j++) {
                HmmFloat_t thing = 1.0;
                thing *= alpha[i][t];
                thing *= _A[i][j];
                thing *= bmap[j][t+1];
                thing *= beta[j][t+1];
                
                denom += thing;
            }
        }
        
        for (i = 0; i < _numStates; i++) {
            for (j = 0; j < _numStates; j++) {
                HmmFloat_t numer = 1.0;
                numer *= alpha[i][t];
                numer *= _A[i][j];
                numer *= bmap[j][t+1];
                numer *= beta[j][t+1];
                
                xi[i][j][t] = numer / denom;
            }
            
        }
        
    }
    
                
    return xi;

}

HmmDataMatrix_t HiddenMarkovModel::getGamma(const Hmm3DMatrix_t & xi,size_t numObs) const {
    /*
    Calculates 'gamma' from xi.
    
    Gamma is a (TxN) numpy array, where gamma[t][i] = the probability of being
    in state 'i' at time 't' given the full observation sequence.
    */
    
    int32_t t,i,j;
    HmmDataMatrix_t gamma = getZeroedMatrix(_numStates, numObs);
    
    for (t = 0; t < numObs; t++) {
        for (i = 0; i < _numStates; i++) {
            for (j = 0; j < _numStates; j++) {
                gamma[i][t] += xi[i][j][t];
            }
        }
    }
    
    return gamma;

}

HmmDataMatrix_t HiddenMarkovModel::reestimateA(const Hmm3DMatrix_t & xi, const HmmDataMatrix_t & gamma,const size_t numObs) const {
    
    int32_t i,j,t;
    HmmDataMatrix_t A = getZeroedMatrix(_numStates, _numStates);
    
    for (i = 0; i < _numStates; i++) {
        HmmFloat_t denom = 0.0;
        
        for (t = 0; t < numObs; t++) {
            denom += gamma[i][t];
        }
    
        for (j = 0; j < numObs; j++) {
            HmmFloat_t numer = 0.0;
            for (t = 0; t < numObs; t++) {
                numer += xi[i][j][t];
            }
            
            A[i][j] = numer / denom;
        }
    }
    
    return A;
    
}

void HiddenMarkovModel::reestimate(const HmmDataMatrix_t & meas) {
    if (meas.empty()) {
        return;
    }
    
    size_t numObs = meas[0].size();
    HmmDataVec_t pi = getUniformVec(_numStates);
    HmmDataMatrix_t logbmap = getLogBMap(meas);
    
    AlphaBetaResult_t alphabeta = getAlphaAndBeta(numObs, pi, logbmap, _A);
    
    Hmm3DMatrix_t xi = getXi(alphabeta,numObs);
    
    HmmDataMatrix_t gamma = getGamma(xi,numObs);
    
    HmmDataMatrix_t newA = reestimateA(xi, gamma, numObs);
    
    ModelVec_t newmodels;
    
    //TODO parallelize
    for (size_t iState = 0; iState < _numStates; iState++) {
        const HmmDataVec_t & gammaForThisState = gamma[iState];
        
        HmmPdfInterface * newModel = _models[iState]->reestimate(gammaForThisState, meas);
        
        newmodels.push_back(newModel);
    }
    
    
    //free up memory of old models
    clearModels();
    
    
    _models = newmodels;
    _A = newA;

    
}



