#include "HiddenMarkovModel.h"
#include "HmmTypes.h"
#include "LogMath.h"
#include "ThreadPool.h"
#include <iostream>
#include "SerializationHelpers.h"
#include <assert.h>

#define MIN_VALUE_FOR_A (1e-1)


#define THREAD_POOL_SIZE (4)
//#define USE_THREADPOOL

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


static Hmm3DMatrix_t getZeroed3dMatrix(size_t numMats, size_t numVecs, size_t vecSize) {
    Hmm3DMatrix_t mtx3;
    mtx3.reserve(numMats);
    
    for (int i = 0; i < numMats; i++) {
        mtx3.push_back(getZeroedMatrix(numVecs, vecSize));
    }
    
    return mtx3;
}


static Hmm3DMatrix_t getLogZeroed3dMatrix(size_t numMats, size_t numVecs, size_t vecSize) {
    (void)getZeroed3dMatrix;
    Hmm3DMatrix_t mtx3;
    mtx3.reserve(numMats);
    
    for (int i = 0; i < numMats; i++) {
        mtx3.push_back(getLogZeroedMatrix(numVecs, vecSize));
    }
    
    return mtx3;
}

static ViterbiPath_t getZeroedPathVec(size_t vecSize) {
    ViterbiPath_t path;
    path.resize(vecSize);
    memset(path.data(),0,sizeof(ViterbiPath_t::value_type)*path.size());
    return path;
}

static ViterbiPathMatrix_t getZeroedPathMatrix(size_t numVecs, size_t vecSize) {
    ViterbiPathMatrix_t mtx;
    
    for (int i = 0; i < numVecs; i++) {
        mtx.push_back(getZeroedPathVec(vecSize));
    }
    
    return mtx;
}

static uint32_t getArgMaxInVec(const HmmDataVec_t & x) {
    HmmFloat_t max = -INFINITY;
    int32_t imax = 0;
    for (int32_t i = 0; i < x.size(); i++) {
        if (x[i] > max) {
            max = x[i];
            imax = i;
        }
    }
    
    //assert(imax >= 0);
    
    return imax;
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


HiddenMarkovModel::HiddenMarkovModel(const HiddenMarkovModel & hmm) {
    *this = hmm;
   
}

HiddenMarkovModel::HiddenMarkovModel(const HmmDataMatrix_t & A)
:_A(A) {
    _numStates = A.size();
    _pi = getUniformVec(_numStates);
}

HiddenMarkovModel::~HiddenMarkovModel() {
    
    clearModels();
    
}

HiddenMarkovModel & HiddenMarkovModel::operator = (const HiddenMarkovModel & hmm) {
    clearModels();
    for (ModelVec_t::const_iterator it = hmm._models.begin();
         it != hmm._models.end(); it++) {
        _models.push_back((*it)->clone(false));
    }
    
    _A = hmm._A;
    _numStates = hmm._numStates;
    _pi = hmm._pi;
    
    return *this;
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
    

#ifdef USE_THREADPOOL

    
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

    
    
#else
    
    
    for (ModelVec_t::const_iterator it = _models.begin(); it != _models.end(); it++) {
        const HmmPdfInterface * ref = *it;
        logbmap.push_back(ref->getLogOfPdf(meas));
    }
    
    
#endif
    
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
            
            if (_A[i][j] > EPSILON) {
                if (A[i][j] <= EPSILON) {
                    A[i][j] = MIN_VALUE_FOR_A;
                }
            }
        }
    }
    
    return A;
    
}

static ViterbiPath_t decodePath(int32_t startidx,const ViterbiPathMatrix_t & paths,const UIntSet_t & restartIndices) {
    size_t len = paths[0].size();
    
    
    ViterbiPath_t path;
    path.resize(len);
    
    path[len-1] = startidx;
    for(int i = len - 2; i >= 0; i--) {
        
        if (restartIndices.find(i + 1) != restartIndices.end()) {
            path[i] = startidx;
        }
        else {
            path[i] = paths[path[i+1]][i];
        }
    }
    
    return path;
}

ViterbiDecodeResult_t HiddenMarkovModel::decodePathAndGetCost(int32_t startidx,const ViterbiPathMatrix_t & paths,const HmmDataMatrix_t & phi, const UIntSet_t & restartIndices) const  {
    size_t numStates = paths.size();
    size_t len = paths[0].size();
    HmmFloat_t cost;
    
    ViterbiPath_t path = decodePath(startidx,paths,restartIndices);
    
    cost = phi[path[len-1]][len-1];
    
    uint32_t numFreeParams = numStates*numStates;
    
    for (ModelVec_t::const_iterator it = _models.begin(); it != _models.end(); it++) {
        numFreeParams += (*it)->getNumberOfFreeParams();
    }
    
    const HmmFloat_t bic = 2*cost + numFreeParams * log(len);

    return ViterbiDecodeResult_t(path,cost,bic);
}


void HiddenMarkovModel::InitializeReestimation(const HmmDataMatrix_t & meas) {
    for (int i = 0; i < 1; i++) {
       reestimateViterbi(meas);
    }
}


HiddenMarkovModel * HiddenMarkovModel::splitState(uint32_t stateToSplit) const {
    int i,j;
    const uint32_t splitIndices[2] = {stateToSplit,_numStates};
    
    //enlarge A by 1 row and 1 column
    HmmDataMatrix_t splitA = _A; //copy

    for (i = 0; i < _numStates; i++) {
        splitA[i].push_back(0.0);
    }
    
    splitA.push_back(getZeroedVec(_numStates + 1));
    
    //fill out new values
    for (i = 0; i < 2; i++) {
        const int idx = splitIndices[i];
        
        //s' --> si
        for (j = 0; j < _numStates; j++) {
            splitA[j][idx] = 0.5 * _A[j][stateToSplit];
        }
    }
    
    for (i = 0; i < 2; i++) {
        const int idx = splitIndices[i];

        HmmDataVec_t & row = splitA[idx];

        for (j = 0; j < row.size(); j++) {
            
            //si --> s'
            if (j != splitIndices[0] && j != splitIndices[1]) {
                row[j] = _A[stateToSplit][j];
            }
        }
    }
    
    //si1 --> si2,, si2 --> si1, etc. etc.
    splitA[splitIndices[0]][splitIndices[0]] = 0.5 * _A[stateToSplit][stateToSplit];
    splitA[splitIndices[0]][splitIndices[1]] = 0.5 * _A[stateToSplit][stateToSplit];
    splitA[splitIndices[1]][splitIndices[0]] = 0.5 * _A[stateToSplit][stateToSplit];
    splitA[splitIndices[1]][splitIndices[1]] = 0.5 * _A[stateToSplit][stateToSplit];


    
    HiddenMarkovModel * splitModel = new HiddenMarkovModel(splitA);
    
    const HmmPdfInterface * modelToSplit = NULL;
    int iModel = 0;
    for (ModelVec_t::const_iterator it = _models.begin(); it != _models.end(); it++) {
        splitModel->addModelForState((*it)->clone(false));
        
        if (iModel == stateToSplit) {
            modelToSplit = *it;
        }
        
        iModel++;
    }
    
    splitModel->addModelForState(modelToSplit->clone(true));
    
    return splitModel;
}



ViterbiDecodeResult_t HiddenMarkovModel::decode(const HmmDataMatrix_t & meas) const {
    int j,i,t;
    
    const HmmDataMatrix_t logbmap = getLogBMap(meas);
    const size_t numObs = meas[0].size();

    HmmDataVec_t costs;
    costs.resize(_numStates);
    
    HmmDataMatrix_t phi = getLogZeroedMatrix(_numStates, numObs);
    ViterbiPathMatrix_t vindices = getZeroedPathMatrix(_numStates, numObs);
    HmmDataMatrix_t logA = _A; //copy
        
    for (j = 0; j < _numStates; j++) {
        for (i = 0; i < _numStates; i++) {
            logA[j][i] = eln(logA[j][i]);
        }
    }
    
    //init
    for (i = 0; i < _numStates; i++) {
        phi[i][0] = elnproduct(logbmap[i][0], eln(_pi[i]));
    }

        

    for (t = 1; t < numObs; t++) {
        for (j = 0; j < _numStates; j++) {
            const HmmFloat_t obscost = logbmap[j][t];
            
            for (i = 0; i < _numStates; i++) {
                costs[i] = elnproduct(logA[i][j], obscost);
            }
            
            for (i = 0; i < _numStates; i++) {
                costs[i] = elnproduct(costs[i], phi[i][t-1]);
            }
            
            const int32_t maxidx = getArgMaxInVec(costs);
            const HmmFloat_t maxval = costs[maxidx];
            
            phi[j][t] = maxval;
            vindices[j][t] = maxidx;
        }
    }
    
    UIntSet_t emptySet;
    const ViterbiDecodeResult_t result = decodePathAndGetCost(0, vindices, phi,emptySet);
    
    
    return result;
    
}

void HiddenMarkovModel::reestimateFromGamma(const HmmDataMatrix_t & gamma, const HmmDataMatrix_t & meas) {
#ifdef USE_THREADPOOL
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
    
    
    //free up memory of old models
    clearModels();
    
    _models.resize(_numStates);
    //go get results and place in models vec
    for(auto && result : newmodels) {
        StateIdxModelPair_t v = result.get();
        _models[v.first] = v.second;
    }
    
    
#else
    {
        ModelVec_t newmodels;
        for (size_t iState = 0; iState < _numStates; iState++) {
            
            const HmmDataVec_t & gammaForThisState = gamma[iState];
            
            HmmPdfInterface * newModel = _models[iState]->reestimate(gammaForThisState, meas);
            
            newmodels.push_back(newModel);
        }
        
        clearModels();
        
        _models = newmodels;
    }
    
#endif
}

ReestimationResult_t HiddenMarkovModel::reestimate(const HmmDataMatrix_t & meas) {
    if (meas.empty()) {
        return ReestimationResult_t();
    }
    
    const size_t numObs = meas[0].size();
    
    const HmmDataMatrix_t logbmap = getLogBMap(meas);
    
    const AlphaBetaResult_t alphabeta = getAlphaAndBeta(numObs, _pi, logbmap, _A);
    
    const Hmm3DMatrix_t logxi = getLogXi(alphabeta,logbmap,numObs);
    
    const HmmDataMatrix_t loggamma = getLogGamma(alphabeta,numObs);
    
    const HmmDataMatrix_t newA = reestimateA(logxi, loggamma, numObs);
    
    HmmDataMatrix_t gamma = getEEXPofMatrix(loggamma);
    
    
    reestimateFromGamma(gamma,meas);

    _A = newA;
    
    for (int i = 0; i < _numStates; i++) {
        _pi[i] = gamma[i][0];
    }
    
    return ReestimationResult_t(-alphabeta.logmodelcost);

}

HmmDataMatrix_t HiddenMarkovModel::getGammaFromViterbiPath(const ViterbiPath_t & path,const size_t numStates,const size_t numObs) const {
    HmmDataMatrix_t gamma = getZeroedMatrix(numStates, numObs);

    for (int t = 0; t < numObs; t++) {
        gamma[path[t]][t] = 1;
    }

    return gamma;
}

HmmDataMatrix_t HiddenMarkovModel::reestimateAFromViterbiPath(const ViterbiPath_t & path, const HmmDataMatrix_t & meas,size_t numObs) const {
    HmmDataMatrix_t A = getZeroedMatrix(_numStates, _numStates);
    
    int t,j,i;
    
    for (t = 1; t < numObs; t++) {
        const int32_t fromidx = path[t-1];
        const int32_t toidx = path[t];
        A[fromidx][toidx] += 1.0;
    }
    
    for (j = 0; j < _numStates; j++) {
        HmmFloat_t sum = 0.0;
        for (i = 0; i < _numStates; i++) {
            sum += A[j][i];
        }
        
        if (sum > EPSILON) {
            for (i = 0; i < _numStates; i++) {
                A[j][i] /= sum;
            }
        }
        
    }
    
    for (j = 0; j < _numStates; j++) {
        for (i = 0; i < _numStates; i++) {
            
            if (_A[j][i] > EPSILON) {
                if (A[j][i] <= EPSILON) {
                    A[j][i] = MIN_VALUE_FOR_A;
                }
            }
            
        }
    }
    
    return A;
    
}


ReestimationResult_t HiddenMarkovModel::reestimateViterbi(const HmmDataMatrix_t & meas) {
    
    const size_t numObs = meas[0].size();
    
    const ViterbiDecodeResult_t res = this->decode(meas);
    
    const HmmDataMatrix_t gamma = getGammaFromViterbiPath(res.path,_numStates,numObs);
    
    reestimateFromGamma(gamma,meas);
    
    _A = reestimateAFromViterbiPath(res.path,meas,numObs);
    
    return ReestimationResult_t(-res.cost);
}

void HiddenMarkovModel::reestimateViterbiSplitState(uint32_t s1, uint32_t s2,const ViterbiPath_t & originalViterbi,const HmmDataMatrix_t & meas) {
    
    uint32_t ti,j,i;
    uint32_t iter;
    
    HmmDataMatrix_t logA = _A; //copy
    
    HmmDataMatrix_t splitlogbmap;
    splitlogbmap.resize(2);
    
    splitlogbmap[0] = _models[s1]->getLogOfPdf(meas);
    splitlogbmap[1] = _models[s2]->getLogOfPdf(meas);

    
    const size_t numObs = meas[0].size();

    for (j = 0; j < _numStates; j++) {
        for (i = 0; i < _numStates; i++) {
            logA[j][i] = eln(logA[j][i]);
        }
    }
    
    HmmDataMatrix_t splitLogA = getZeroedMatrix(2, 2);
    splitLogA[0][0] = logA[s1][s1];
    splitLogA[1][0] = logA[s2][s1];
    splitLogA[0][1] = logA[s1][s2];
    splitLogA[1][1] = logA[s2][s2];

    
    
    UIntVec_t myTimeIndices;
    myTimeIndices.reserve(numObs);
    
    //find times in which we think the state is one of our split states
    for (ti = 0; ti < numObs; ti++) {
        const uint32_t idx = originalViterbi[ti];
        if (idx == s1 || idx == s2) {
            myTimeIndices.push_back(ti);
        }
    }
    
    if (myTimeIndices.empty()) {
        std::cout << "split state " << s1 + 1 << " of " << _numStates - 1 << " failed because no obs belong to this state" << std::endl;
        return;
    }
    
    for (iter = 0; iter < 5; iter++) {
        
        ViterbiPathMatrix_t vindices = getZeroedPathMatrix(2, myTimeIndices.size());
        HmmDataMatrix_t phi = getLogZeroedMatrix(2, myTimeIndices.size());
        UIntSet_t restartIndices;
        restartIndices.reserve(myTimeIndices.size());
        int32_t previdx = -1;
        //skip the first time step, who cares
        for (ti = 0; ti < myTimeIndices.size(); ti++) {
            
            const int32_t tidx = myTimeIndices[ti];
            
            if (tidx == 0) {
                continue; //todo implement this, but not very important
            }
            
            //contiguous?
            HmmDataVec_t costs = getLogZeroedVec(2);
            if (previdx == tidx - 1) {
                for (j = 0; j < 2; j++) {
                    const HmmFloat_t obscost = splitlogbmap[j][ti];
                    
                    for (i = 0; i < 2; i++) {
                        costs[i] = elnproduct(splitLogA[i][j], obscost);
                    }
                    
                    for (i = 0; i < 2; i++) {
                        costs[i] = elnproduct(costs[i], phi[i][ti-1]);
                    }
                    
                    const uint32_t maxidx = getArgMaxInVec(costs);
                    const HmmFloat_t maxval = costs[maxidx];
                    
                    phi[j][ti] = maxval;
                    vindices[j][ti] = maxidx;
                }
                
            }
            else {
                //otherwise, start afresh
                const uint32_t comingFromState = originalViterbi[tidx - 1];
                const uint32_t goingToState = originalViterbi[tidx];
                assert(goingToState == s1 || goingToState == s2);
                phi[0][ti] = elnproduct(logA[comingFromState][goingToState],splitlogbmap[0][tidx]);
                phi[1][ti] = elnproduct(logA[comingFromState][goingToState],splitlogbmap[1][tidx]);
                restartIndices.insert(ti);
            }
            
            previdx = tidx;
        }
        
        
        const ViterbiDecodeResult_t res = decodePathAndGetCost(0, vindices, phi,restartIndices);
        
        const HmmDataMatrix_t gamma = getGammaFromViterbiPath(res.path,2,myTimeIndices.size());

        HmmPdfInterface * r1 = _models[s1]->reestimate(gamma[0], meas);
        HmmPdfInterface * r2 = _models[s2]->reestimate(gamma[1], meas);
        
        delete _models[s1];
        delete _models[s2];
        
        _models[s1] = r1;
        _models[s2] = r2;
        
        
    }
    
   
    
}

HmmFloat_t HiddenMarkovModel::getModelCost(const HmmDataMatrix_t & meas) const {
    const size_t numObs = meas[0].size();

    const HmmDataMatrix_t logbmap = getLogBMap(meas);
    
    const AlphaBetaResult_t res = getAlphaAndBeta(numObs, _pi, logbmap, _A);
    
    return -res.logmodelcost;
}



void  HiddenMarkovModel::enlargeWithVSTACS(const HmmDataMatrix_t & meas, uint32_t numToGrow) {
    typedef std::vector<HiddenMarkovModel *> HmmVec_t;
    uint32_t numStates = _numStates;
    HiddenMarkovModel * best = new HiddenMarkovModel(*this); //init
    
    for (uint32_t iter = 0; iter < numToGrow; iter++) {
        HmmVec_t hmms;

        //converge to something with viterbi training
        for (int i = 0; i < 5; i++) {
            best->reestimateViterbi(meas);
        }
        for (int i = 0; i < 2; i++) {
            best->reestimate(meas);
        }

        
        //best->reestimate(meas); //finishing touches
        
        const ViterbiDecodeResult_t res = best->decode(meas);
        
        
        for (uint32_t iState = 0; iState < numStates; iState++) {
            HiddenMarkovModel * newSplitModel = best->splitState(iState);
            hmms.push_back(newSplitModel);
        }
        
        //TODO PARALLELIZE
        HmmDataVec_t costs;
        costs.resize(numStates);
        std::cout << "splitting  " << numStates << " states." << std::endl;
        for (uint32_t iState = 0; iState < numStates; iState++) {
            hmms[iState]->reestimateViterbiSplitState(iState, numStates, res.path, meas);
            
            const ViterbiDecodeResult_t res = hmms[iState]->decode(meas);
            
            costs[iState] = res.bic;
        }
        
        std::cout << costs << std::endl;
        
        const uint32_t bestidx = getArgMaxInVec(costs);
        
        std::cout << "picked split of state " << bestidx << std::endl;
        
        delete best; //replace with new
        best = hmms[bestidx];
        
        //delete the models that were not the best
        for (HmmVec_t::iterator it = hmms.begin(); it != hmms.end(); it++) {
            if (*it != best) {
                delete *it;
            }
        }
        
        numStates++;
    }
    
    for (int i = 0; i < 2; i++) {
        best->reestimate(meas); //converge to something with viterbi training
    }
    
    //best->reestimate(meas); //finishing touches
    
    *this = *best;
    
    delete best;
    
    
}




