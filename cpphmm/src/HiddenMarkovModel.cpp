#include "HiddenMarkovModel.h"
#include "HmmTypes.h"
#include <math.h>
#include "ThreadPool.h"
#include <iostream>

#define MIN_NORMALIZING_VALUE (1e-8)
#define MIN_LOG_BMAP (-10)
#define MIN_XI_LOG_RATIO (-15)

#define THREAD_POOL_SIZE (4)

typedef std::pair<int32_t,HmmPdfInterface *> StateIdxModelPair_t;
typedef std::pair<int32_t,HmmDataVec_t> StateIdxPdfEvalPair_t;

typedef std::vector<std::future<StateIdxModelPair_t>> FutureModelVec_t;
typedef std::vector<std::future<StateIdxPdfEvalPair_t>> FuturePdfEvalVec_t;


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

static void printMat(const std::string & name, const HmmDataMatrix_t & mat) {
    
    std::cout << name << std::endl;
    
    for (HmmDataMatrix_t::const_iterator it = mat.begin(); it != mat.end(); it++) {
        bool first = true;
        for (HmmDataVec_t::const_iterator itvec2 = (*it).begin(); itvec2 != (*it).end(); itvec2++) {
            if (!first) {
                std::cout << ",";
            }
            
            std::cout << *itvec2;
            
            
            first = false;
        }
        
        std::cout << std::endl;
    }
    
    
}


HiddenMarkovModel::HiddenMarkovModel(const HmmDataMatrix_t & A)
:_A(A) {
    _numStates = A.size();
    _pi = getUniformVec(_numStates);
}

HiddenMarkovModel::~HiddenMarkovModel() {
    
    clearModels();
    
}

std::string HiddenMarkovModel::serializeToJson() const {
    return _models[0]->serializeToJson();
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
        }
    }
    for (int j = 0; j < numStates; j++) {
        HmmDataVec_t & brow = bmap[j];
        
        for (int i = 0; i < brow.size(); i++) {
            
            if (brow[i] < MIN_LOG_BMAP) {
                brow[i] = MIN_LOG_BMAP;
            }
            
            brow[i] = exp(brow[i]);
        }
    }
    
    
    return bmap;

}



static void printVec(const std::string & name, const HmmDataVec_t & vec) {
    bool first = true;
    for (HmmDataVec_t::const_iterator itvec2 = vec.begin(); itvec2 != vec.end(); itvec2++) {
        if (!first) {
            std::cout << ",";
        }
        
        std::cout << *itvec2;
        
        
        first = false;
    }
    std::cout << std::endl;

}

HmmDataMatrix_t HiddenMarkovModel::getLogBMap(const HmmDataMatrix_t & meas) const {
    HmmDataMatrix_t logbmap;
    
    
    ModelVec_t localModels = _models; //copies all the pointers
    FuturePdfEvalVec_t newevals;
    
    
    {
        //destructor of threadpool joins all threads
        ThreadPool pool(THREAD_POOL_SIZE);
        
        for (int32_t iState = 0; iState < _numStates; iState++) {
            newevals.emplace_back(
                                   pool.enqueue([iState,&meas,&localModels] {
                return std::make_pair(iState,localModels[iState]->getLogOfPdf(meas));
            }));
        }
    }
    
    
    logbmap.resize(_numStates);
    
    //go get results and place in models vec
    for(auto && result : newevals) {
        StateIdxPdfEvalPair_t v = result.get();
        logbmap[v.first] = v.second;
    }

    
    
    
    
    //TODO parallelize
    /*
    for (ModelVec_t::const_iterator it = _models.begin(); it != _models.end(); it++) {
        const HmmPdfInterface * ref = *it;
        logbmap.push_back(ref->getLogOfPdf(meas));
    }
     */
    
    return logbmap;
}

static HmmFloat_t subtracMaxInVec(HmmDataVec_t & vec) {
    HmmFloat_t max = -INFINITY;
    
    for (int i = 0; i < vec.size(); i++) {
        if (vec[i] > max) {
            max = vec[i];
        }
    }
    
    for (int i = 0; i < vec.size(); i++) {
        vec[i] -= max;
    }
    
    return max;
}

AlphaBetaResult_t HiddenMarkovModel::getAlphaAndBeta(int32_t numObs,const HmmDataVec_t & pi, const HmmDataMatrix_t & logbmap, const HmmDataMatrix_t & A) const {
    /*
    Calculates 'alpha' the forward variable.
    
    The alpha variable is a numpy array indexed by time, then state (NxT).
    alpha[i][t] = the probability of being in state 'i' after observing the
    first t symbols.
    */
    int t,j,i;
    HmmDataMatrix_t logalpha = getZeroedMatrix(_numStates,numObs);
    HmmDataMatrix_t logbeta = getZeroedMatrix(_numStates,numObs);
    HmmDataVec_t tempvec = getZeroedVec(_numStates);

    HmmFloat_t logmaximum = 0;
    HmmDataMatrix_t bmap = getNormalizedBMap(logbmap,logmaximum);
    
    HmmDataMatrix_t logA = A;
    
    for (j = 0; j < _numStates; j++) {
        for (i = 0; i < _numStates; i++) {
            logA[j][i] = log(logA[j][i]);
        }
    }
    
    
    //init stage - alpha_1(x) = pi(x)b_x(O1)

    for (j = 0; j < _numStates; j++) {
        logalpha[j][0] = log(pi[j]) + logbmap[j][0];
    }
    
    
    for (t = 1; t < numObs; t++) {
        for (j = 0; j < _numStates; j++) {
            
            for (i = 0; i < _numStates; i++) {
                tempvec[i] = logalpha[i][t-1] + logA[i][j];
                //alpha[j][t] += alpha[i][t-1]*A[i][j];
            }
            
            const HmmFloat_t max = subtracMaxInVec(tempvec);
            HmmFloat_t temp = 0.0;
            
            for (i = 0; i < _numStates; i++) {
                temp += exp(tempvec[i]);
            }
            logalpha[j][t] = log(temp) + logbmap[j][t] + max;
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
    for (int s = 0; s < _numStates; s++) {
        logbeta[s][numObs - 1] = 0.0;
    }
    

    
    for (t = numObs - 2; t >= 0; t--) {
        for (i = 0; i < _numStates; i++) {
            for (j = 0;  j < _numStates; j++) {
                tempvec[j] = logA[i][j] + logbmap[j][t+1] + logbeta[j][t+1];
                //beta[i][t] += A[i][j]*bmap[j][t+1] * beta[j][t+1];
            }
            
            const HmmFloat_t max = subtracMaxInVec(tempvec);
            HmmFloat_t temp = 0.0;
            
            for (j = 0; j < _numStates; j++) {
                temp += exp(tempvec[j]);
            }
            
            logbeta[i][t] = log(temp) + max;
            
        }
    }
    
    for (i = 0; i < _numStates; i++) {
        tempvec[i] = logalpha[i][numObs-1];
    }
    
    const HmmFloat_t max = subtracMaxInVec(tempvec);
    HmmFloat_t temp = 0.0;
    
    for (i = 0; i < _numStates; i++) {
        temp += exp(tempvec[i]);
    }

    
    
    const AlphaBetaResult_t result(logalpha,logbeta,logA,log(temp) + max);
    
    (void)printMat;
    (void)printVec;
    //printVec("c",c);
    //printMat("alpha",alpha);
    //printMat("beta",beta);

    return result;
    
    

}

Hmm3DMatrix_t HiddenMarkovModel::getXi(const AlphaBetaResult_t & alphabeta,const HmmDataMatrix_t & logbmap,size_t numObs) const {
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
    Hmm3DMatrix_t xi = getZeroed3dMatrix(_numStates,_numStates, numObs);
    HmmDataVec_t tempvec = getZeroedVec(_numStates);
    HmmDataVec_t logdenomvec = getZeroedVec(_numStates);
    HmmFloat_t temp = 0.0;
    HmmFloat_t max;
    
    for (t = 0; t < numObs - 1; t++) {
        HmmFloat_t logdenom;
        for (i = 0; i < _numStates; i++) {
            for (j = 0; j < _numStates; j++) {
                HmmFloat_t thing = 0.0;
                thing += logalpha[i][t];
                thing += logA[i][j];
                thing += logbmap[j][t+1];
                thing += logbeta[j][t+1];
                
                tempvec[j] = thing;
            }
            
            temp = 0.0;
            max = subtracMaxInVec(tempvec);
            
            for (j = 0; j < _numStates; j++) {
                temp += exp(tempvec[j]);
            }
            
            logdenomvec[i] = log(temp) + max;
            
        }
        
        temp = 0.0;
        max = subtracMaxInVec(logdenomvec);
        
        for (j = 0; j < _numStates; j++) {
            temp += exp(tempvec[j]);
        }
        
        logdenom = log(temp) + max;
        
        for (i = 0; i < _numStates; i++) {
            for (j = 0; j < _numStates; j++) {
                HmmFloat_t lognumer = 0.0;
                lognumer += logalpha[i][t];
                lognumer += logA[i][j];
                lognumer += logbmap[j][t+1];
                lognumer += logbeta[j][t+1];
                
                temp = lognumer - logdenom;
                
                if (temp < MIN_XI_LOG_RATIO) {
                    temp = MIN_XI_LOG_RATIO;
                }
                
               
                temp = exp(temp);
                
                xi[i][j][t] = temp;
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
    
        for (j = 0; j < _numStates; j++) {
            HmmFloat_t numer = 0.0;
            for (t = 0; t < numObs; t++) {
                numer += xi[i][j][t];
            }
            
            A[i][j] = numer / denom;
        }
    }
    
    return A;
    
}

ReestimationResult_t HiddenMarkovModel::reestimate(const HmmDataMatrix_t & meas) {
    if (meas.empty()) {
        return ReestimationResult_t();
    }
    
    size_t numObs = meas[0].size();
    HmmDataMatrix_t logbmap = getLogBMap(meas);
    
    const AlphaBetaResult_t alphabeta = getAlphaAndBeta(numObs, _pi, logbmap, _A);
    
    const Hmm3DMatrix_t xi = getXi(alphabeta,logbmap,numObs);
    
    const HmmDataMatrix_t gamma = getGamma(xi,numObs);
    
    const HmmDataMatrix_t newA = reestimateA(xi, gamma, numObs);
    
    
    const ModelVec_t localModels = _models; //copies all the pointers
    FutureModelVec_t newmodels;
    
    
    {
        //destructor of threadpool joins all threads
        ThreadPool pool(THREAD_POOL_SIZE);
        
        for (int32_t iState = 0; iState < _numStates; iState++) {
            newmodels.emplace_back(
                pool.enqueue([iState,&gamma,&meas,&localModels] {
                return std::make_pair(iState,localModels[iState]->reestimate(gamma[iState], meas));
            }));
        }
    }
    
    
    /*
    //TODO parallelize
    for (size_t iState = 0; iState < _numStates; iState++) {
        const HmmDataVec_t & gammaForThisState = gamma[iState];
        
        HmmPdfInterface * newModel = _models[iState]->reestimate(gammaForThisState, meas);
        
        newmodels.push_back(newModel);
    }
     */
    
    
    //free up memory of old models
    clearModels();
    
    _models.resize(_numStates);
    //go get results and place in models vec
    for(auto && result : newmodels) {
        StateIdxModelPair_t v = result.get();
        _models[v.first] = v.second;
    }
    
    _A = newA;
    
    for (int i = 0; i < _numStates; i++) {
        _pi[i] = gamma[i][0];
        
        if (_pi[i] < 1e-6) {
            _pi[i] = 1e-6;
        }
    }
    

    
    
    return ReestimationResult_t(-alphabeta.logmodelcost);

}




