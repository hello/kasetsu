#include "HiddenMarkovModel.h"
#include "HmmTypes.h"
#include "LogMath.h"
#include "ThreadPool.h"
#include <iostream>
#include "SerializationHelpers.h"


#define THREAD_POOL_SIZE (4)

typedef std::pair<int32_t,HmmPdfInterface *> StateIdxModelPair_t;
typedef std::pair<int32_t,HmmDataVec_t> StateIdxPdfEvalPair_t;

typedef std::vector<std::future<StateIdxModelPair_t>> FutureModelVec_t;
typedef std::vector<std::future<StateIdxPdfEvalPair_t>> FuturePdfEvalVec_t;


static HmmDataMatrix_t getEEXPofMatrix(const HmmDataMatrix_t & x) {
    HmmDataMatrix_t y = x;
    
    for (HmmDataMatrix_t::iterator ivec = y.begin();
         ivec != y.end(); ivec++) {
        HmmDataVec_t & row = *ivec;
        
        for (int i = 0; i < row.size(); i++) {
            row[i] = eexp(row[i]);
        }
    }
    
    return y;
}

static HmmDataVec_t getZeroedVec(size_t vecSize) {
    HmmDataVec_t vec;
    vec.resize(vecSize);
    memset(vec.data(),0,sizeof(HmmFloat_t) * vecSize);
    return vec;
}

static HmmDataVec_t getLogZeroedVec(size_t vecSize) {
    HmmDataVec_t vec;
    vec.resize(vecSize);
    
    for (int i = 0; i < vec.size(); i++) {
        vec[i] = LOGZERO;
    }
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

static HmmDataMatrix_t getLogZeroedMatrix(size_t numVecs, size_t vecSize) {
    HmmDataMatrix_t mtx;
    mtx.resize(numVecs);
    
    //allocate and zero out
    for(int j = 0; j < numVecs; j++) {
        mtx[j] = getLogZeroedVec(vecSize);
    }
    
    return mtx;
}

#if 0
static Hmm3DMatrix_t getZeroed3dMatrix(size_t numMats, size_t numVecs, size_t vecSize) {
    Hmm3DMatrix_t mtx3;
    mtx3.reserve(numMats);
    
    for (int i = 0; i < numMats; i++) {
        mtx3.push_back(getZeroedMatrix(numVecs, vecSize));
    }
    
    return mtx3;
}
#endif

static Hmm3DMatrix_t getLogZeroed3dMatrix(size_t numMats, size_t numVecs, size_t vecSize) {
    Hmm3DMatrix_t mtx3;
    mtx3.reserve(numMats);
    
    for (int i = 0; i < numMats; i++) {
        mtx3.push_back(getLogZeroedMatrix(numVecs, vecSize));
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
    
    typedef std::vector<std::string> StringVec_t;
    StringVec_t bigarray;
    
    std::string A = vecToJsonArray<HmmDataMatrix_t,VecOfVecsSerializationAdapter<HmmDataMatrix_t::value_type>>(_A);
    
    A = makeKeyValue("A",A);
    
    std::string models = vecToJsonArray<ModelVec_t,PdfInterfaceSerializationAdapter<ModelVec_t::value_type>>(_models);
    
    models = makeKeyValue("models",models);
    
    std::string pi = makeKeyValue("pi",vecToJsonArray(_pi));
    
    std::string stuff =  "\"params\": {\"natural_light_filter_start_hour\": 16, \"on_bed_states\": [4, 5, 6, 7, 8, 9, 10], \"users\": \"1086,1050,1052,1053,1072,1071,1,1038,1063,1012,1013,1043,1310,1629,1025,1061,1060,1049,1062,1648,1067,1609,1005,1002,1001\", \"num_model_params\": 77, \"natural_light_filter_stop_hour\": 4, \"pill_magnitude_disturbance_threshold_lsb\": 15000, \"sleep_states\": [6, 7, 8], \"enable_interval_search\": true, \"model_name\": \"default\", \"audio_disturbance_threshold_db\": 70.0 , \"meas_period_minutes\" : 15}";
    
    return makeObj(makeKeyValue("default",makeObj(A + "," + models + "," + pi + "," + stuff)));
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


AlphaBetaResult_t HiddenMarkovModel::getAlphaAndBeta(int32_t numObs,const HmmDataVec_t & pi, const HmmDataMatrix_t & logbmap, const HmmDataMatrix_t & A) const {
    /*
    Calculates 'alpha' the forward variable.
    
    The alpha variable is a numpy array indexed by time, then state (NxT).
    alpha[i][t] = the probability of being in state 'i' after observing the
    first t symbols.
    */
    int t,j,i;
    HmmDataMatrix_t logalpha = getLogZeroedMatrix(_numStates,numObs);
    HmmDataMatrix_t logbeta = getLogZeroedMatrix(_numStates,numObs);
    HmmFloat_t temp;
    HmmDataMatrix_t logA = A; //copy
    
    for (j = 0; j < _numStates; j++) {
        for (i = 0; i < _numStates; i++) {
            logA[j][i] = eln(logA[j][i]);
        }
    }
    
    
    //init stage - alpha_1(x) = pi(x)b_x(O1)

    for (j = 0; j < _numStates; j++) {
        logalpha[j][0] = elnproduct(eln(pi[j]), logbmap[j][0]);
    }
    
    
    for (t = 1; t < numObs; t++) {
        for (j = 0; j < _numStates; j++) {
            temp = LOGZERO;
            
            for (i = 0; i < _numStates; i++) {
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
    for (int s = 0; s < _numStates; s++) {
        logbeta[s][numObs - 1] = 0.0;
    }
    

    
    for (t = numObs - 2; t >= 0; t--) {
        for (i = 0; i < _numStates; i++) {
            temp = LOGZERO;
            for (j = 0;  j < _numStates; j++) {
                const HmmFloat_t tempval  = elnproduct(logbmap[j][t+1], logbeta[j][t+1]);
                const HmmFloat_t tempval2 = elnproduct(tempval, logA[i][j]);
                temp = elnsum(temp,tempval2);
                //beta[i][t] += A[i][j]*bmap[j][t+1] * beta[j][t+1];
            }
            
            logbeta[i][t] = temp;
            
        }
    }
    
    temp = LOGZERO;
    for (i = 0; i < _numStates; i++) {
        temp = elnsum(temp,logalpha[i][numObs-1]);
    }
    
    
    const AlphaBetaResult_t result(logalpha,logbeta,logA,temp);
    
    (void)printMat;
    (void)printVec;
    //printVec("c",c);
    //printMat("alpha",alpha);
    //printMat("beta",beta);

    return result;
    
    

}

Hmm3DMatrix_t HiddenMarkovModel::getLogXi(const AlphaBetaResult_t & alphabeta,const HmmDataMatrix_t & logbmap,size_t numObs) const {
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
    Hmm3DMatrix_t logxi = getLogZeroed3dMatrix(_numStates,_numStates, numObs);
    HmmDataVec_t tempvec = getZeroedVec(_numStates);
    HmmDataVec_t logdenomvec = getZeroedVec(_numStates);
    HmmFloat_t normalizer;
    
    for (t = 0; t < numObs - 1; t++) {
        normalizer = LOGZERO;
        
        for (i = 0; i < _numStates; i++) {
            for (j = 0; j < _numStates; j++) {
                
                const HmmFloat_t tempval1 = elnproduct(logalpha[i][t], logA[i][j]);
                const HmmFloat_t tempval2 = elnproduct(logbmap[j][t+1], logbeta[j][t+1]);
                const HmmFloat_t tempval3 = elnproduct(tempval1,tempval2);
                
                logxi[i][j][t] = tempval3;
                
                normalizer = elnsum(tempval3, normalizer);
            }
        }
        
        
        for (i = 0; i < _numStates; i++) {
            for (j = 0; j < _numStates; j++) {
                logxi[i][j][t] = elnproduct(logxi[i][j][t], -normalizer);
            }
            
        }
        
    }
    
    return logxi;

}

HmmDataMatrix_t HiddenMarkovModel::getLogGamma(const AlphaBetaResult_t & alphabeta,size_t numObs) const {
    /*
    Calculates 'gamma' from xi.
    
    Gamma is a (TxN) numpy array, where gamma[t][i] = the probability of being
    in state 'i' at time 't' given the full observation sequence.
    */
    
    int32_t t,i;
    HmmFloat_t normalizer;
    HmmFloat_t temp;
    HmmDataMatrix_t loggamma = getLogZeroedMatrix(_numStates, numObs);
    
    for (t = 0; t < numObs; t++) {
        normalizer = LOGZERO;
        for (i = 0; i < _numStates; i++) {
            temp = elnproduct(alphabeta.logalpha[i][t], alphabeta.logbeta[i][t]);
            loggamma[i][t] = temp;
            normalizer = elnsum(normalizer, temp);
        }
        
        
        for (i = 0; i < _numStates; i++) {
            loggamma[i][t] = elnproduct(loggamma[i][t], -normalizer);
        }
    }
    
    return loggamma;

}

HmmDataMatrix_t HiddenMarkovModel::reestimateA(const Hmm3DMatrix_t & logxi, const HmmDataMatrix_t & loggamma,const size_t numObs) const {
    
    int32_t i,j,t;
    HmmDataMatrix_t A = getZeroedMatrix(_numStates, _numStates);
    
    for (i = 0; i < _numStates; i++) {
        HmmFloat_t denom = LOGZERO;
        
        for (t = 0; t < numObs; t++) {
            denom = elnsum(denom, loggamma[i][t]) ;
        }
    
        for (j = 0; j < _numStates; j++) {
            HmmFloat_t numer = LOGZERO;
            for (t = 0; t < numObs; t++) {
                numer = elnsum(numer,logxi[i][j][t]);
            }
            
            A[i][j] = eexp(elnproduct(numer, -denom));
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
    
    const Hmm3DMatrix_t logxi = getLogXi(alphabeta,logbmap,numObs);
    
    const HmmDataMatrix_t loggamma = getLogGamma(alphabeta,numObs);
    
    const HmmDataMatrix_t newA = reestimateA(logxi, loggamma, numObs);
    
    HmmDataMatrix_t gamma = getEEXPofMatrix(loggamma);
    
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
    }
    
    return ReestimationResult_t(-alphabeta.logmodelcost);

}




