#include "HiddenMarkovModel.h"
#include "HmmTypes.h"
#include "LogMath.h"
#include "ThreadPool.h"
#include <iostream>
#include "SerializationHelpers.h"
#include <assert.h>
#include <iomanip>


#define MIN_VALUE_FOR_A (1e-6)

#define NUM_REESTIMATIONS_FOR_INTIAL_GUESS_PER_ITER (0)
#define MAX_NUM_REESTIMATIONS_PER_ITER (10)
#define MIN_NUM_REESTIMATIONS (0)

#define NUM_SPLIT_STATE_VITERBI_ITERATIONS (1)

#define MIN_FRAC_IN_STATE_TO_SPLIT (0.5)


#define THREAD_POOL_SIZE (4)
//#define USE_THREADPOOL
#define QUIT_TRAINING_IF_NO_IMPROVEMENT
#define QUIT_ENLARGING_IF_NO_IMRPOVEMENT_SEEN

typedef std::pair<int32_t,HmmPdfInterface *> StateIdxModelPair_t;
typedef std::pair<int32_t,HmmDataVec_t> StateIdxPdfEvalPair_t;
typedef std::pair<int32_t,HmmFloat_t> StateIdxCostPair_t;

typedef std::vector<std::future<StateIdxModelPair_t>> FutureModelVec_t;
typedef std::vector<std::future<StateIdxPdfEvalPair_t>> FuturePdfEvalVec_t;
typedef std::vector<std::future<StateIdxCostPair_t>> FutureCostVec_t;

typedef std::vector<HiddenMarkovModel *> HmmVec_t;


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
    
    std::cout << std::fixed << std::setprecision(2) << name << std::endl;
    
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

static HmmDataVec_t getFractionInEachState(uint32_t numStates,const ViterbiPath_t & path) {
    HmmDataVec_t fracInEachState;
    fracInEachState.resize(numStates);
    
    
    for (uint32_t iState = 0; iState < numStates; iState++) {
        uint32_t count = 0;
        for (uint32_t t = 0; t < path.size(); t++) {
            if (path[t] == iState) {
                count++;
            }
        }
        
        fracInEachState[iState] = (HmmFloat_t)count / (HmmFloat_t)path.size();
    }
    
    return fracInEachState;
    
}


HiddenMarkovModel::HiddenMarkovModel(const HiddenMarkovModel & hmm) {
    *this = hmm;
   
}

HiddenMarkovModel::HiddenMarkovModel(const HmmDataMatrix_t & A,const UIntVec_t & groupsByStateNumber)
:_A(A)
,_groups(groupsByStateNumber){
    _numStates = A.size();
    _pi = getUniformVec(_numStates);
    
    if (_groups.empty()) {
        _groups.push_back(0);
    }
}

//for creating seed models
HiddenMarkovModel::HiddenMarkovModel(const UIntVec_t & groupsByStateNumber)
:_groups(groupsByStateNumber) {

    _numStates = groupsByStateNumber.size();
    
    _pi = getUniformVec(_numStates);
    
    //initialize sparsely connected A
    _A = getZeroedMatrix(_numStates, _numStates);
    
//   / HmmFloat_t edgeAlpha = 1.0 / 2.0;
    HmmFloat_t alpha = 1.0 / 3.0;
    
    if(_numStates == 1) {
        alpha = 1.0;
    }
    else if (_numStates == 2) {
        alpha = 0.5;
    }
    
    for (int i = 0; i < _numStates; i++) {
        for (int j = 0; j < _numStates; j++) {
            int diff = i - j;
            
            
            if (diff <= 1 && diff >= -1) {
                if (j == 0 || j == _numStates - 1) {
                    _A[j][i] = alpha;

                }
                else {
                    _A[j][i] = alpha;
                }
            }
            
            
        }
    }
    
    //circular connection
    _A[_numStates - 1][0] = alpha;
    _A[0][_numStates - 1] = alpha;
    
    printMat("A", _A);
}


HiddenMarkovModel::~HiddenMarkovModel() {
    
    
}

HiddenMarkovModel & HiddenMarkovModel::operator = (const HiddenMarkovModel & hmm) {
    _models.clear();
    
    for (ModelVec_t::const_iterator it = hmm._models.begin();
         it != hmm._models.end(); it++) {
        _models.push_back((*it)->clone(false));
    }
    
    _A = hmm._A;
    _numStates = hmm._numStates;
    _pi = hmm._pi;
    _groups = hmm._groups;
    
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


void HiddenMarkovModel::addModelForState(HmmPdfInterfaceSharedPtr_t model) {
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

HmmDataMatrix_t HiddenMarkovModel::getLogBMap(const ModelVec_t & models, const HmmDataMatrix_t & meas) const {
    HmmDataMatrix_t logbmap;
    
    
    FuturePdfEvalVec_t newevals;
    

#ifdef USE_THREADPOOL

    
    {
        //destructor of threadpool joins all threads
        ThreadPool pool(THREAD_POOL_SIZE);
        
        for (int32_t iState = 0; iState < _numStates; iState++) {
            newevals.emplace_back(
                                   pool.enqueue([iState,&meas,&models] {
                return std::make_pair(iState,models[iState]->getLogOfPdf(meas));
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
    
    
    for (ModelVec_t::const_iterator it = models.begin(); it != models.end(); it++) {
        const HmmPdfInterface * ref = (*it).get();
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
                if (A[i][j] <= MIN_VALUE_FOR_A) {
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

    const size_t len = paths[0].size();

    
    //get viterbi path
    ViterbiPath_t path = decodePath(startidx,paths,restartIndices);
    
    //compute cost stuff
    const HmmFloat_t cost = phi[path[len-1]][len-1];
    
    //really -bic

    const HmmFloat_t bic = 2*cost - this->getNumberOfFreeParams() * log(len);

    return ViterbiDecodeResult_t(path,cost,bic);
}


HiddenMarkovModel * HiddenMarkovModel::splitState(uint32_t stateToSplit) const {
    int i,j;
    const uint32_t splitIndices[2] = {stateToSplit,_numStates};
    const uint32_t myGroup = _groups[stateToSplit];
    
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

    std::stringstream ss;
    ss << "splitA - " << stateToSplit;
    //printMat(ss.str(), splitA);
    

    //create the new split model
    UIntVec_t newgroups = _groups;
    newgroups.push_back(myGroup);
    
    HiddenMarkovModel * splitModel = new HiddenMarkovModel(splitA,newgroups);
    
    HmmPdfInterfaceSharedPtr_t modelToSplit;
    
    int iModel = 0;
    for (ModelVec_t::const_iterator it = _models.begin(); it != _models.end(); it++) {
        
        splitModel->addModelForState((*it)->clone(false));
        
        if (iModel == stateToSplit) {
            modelToSplit = (*it).get()->clone(false);
        }
        
        iModel++;
    }
    
   // std::cout << newgroups << std::endl;
    splitModel->addModelForState(modelToSplit->clone(true));
    
    return splitModel;
}



ViterbiDecodeResult_t HiddenMarkovModel::decode(const HmmDataMatrix_t & meas) const {
    int j,i,t;
    
    const HmmDataMatrix_t logbmap = getLogBMap(_models,meas);
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

ModelVec_t HiddenMarkovModel::reestimateFromGamma(const HmmDataMatrix_t & gamma, const HmmDataMatrix_t & meas) const {
    
    ModelVec_t updatedModels;
    
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
    

    updatedModels.resize(_numStates);
    //go get results and place in models vec
    for(auto && result : newmodels) {
        StateIdxModelPair_t v = result.get();
        updatedModels[v.first] = v.second;
    }
    
    
#else
    {
        for (size_t iState = 0; iState < _numStates; iState++) {
            
            const HmmDataVec_t & gammaForThisState = gamma[iState];
            
            HmmPdfInterfaceSharedPtr_t newModel = _models[iState]->reestimate(gammaForThisState, meas);
            
            updatedModels.push_back(newModel);
        }
        
    }
    
#endif
    
    return updatedModels;
}

ReestimationResult_t HiddenMarkovModel::reestimate(const HmmDataMatrix_t & meas,bool dontReestimateIfScoreDidNotImprove) {
    if (meas.empty()) {
        return ReestimationResult_t();
    }
    
    const size_t numObs = meas[0].size();
    
    const HmmDataMatrix_t logbmap = getLogBMap(_models,meas);
    
    const AlphaBetaResult_t alphabeta = getAlphaAndBeta(numObs, _pi, logbmap, _A);
    
    const Hmm3DMatrix_t logxi = getLogXi(alphabeta,logbmap,numObs);
    
    const HmmDataMatrix_t loggamma = getLogGamma(alphabeta,numObs);
    
    const HmmDataMatrix_t newA = reestimateA(logxi, loggamma, numObs);
    
    
    HmmDataMatrix_t gamma = getEEXPofMatrix(loggamma);
    
    HmmDataVec_t newPi = getZeroedVec(_numStates);
    
    for (int i = 0; i < _numStates; i++) {
        newPi[i] = gamma[i][0];
    }
    
    
    ModelVec_t newModels = reestimateFromGamma(gamma,meas);
    
    AlphaBetaResult_t alphabeta2 = alphabeta;
    
    //if you care about the score improving
    if (dontReestimateIfScoreDidNotImprove) {
    
    
        const HmmDataMatrix_t logbmap2 = getLogBMap(newModels,meas);

        AlphaBetaResult_t alphabeta2 = getAlphaAndBeta(numObs, _pi, logbmap2, newA);
        
        if (alphabeta2.logmodelcost <= alphabeta.logmodelcost) {
            
            return ReestimationResult_t();
            
        }
    }
    
    //otherwise.... full steam ahead
    _models.clear();
    
    for (ModelVec_t::iterator it = newModels.begin(); it != newModels.end(); it++) {
        addModelForState((*it)->clone(false));
    }

    
    _A = newA;

    _pi = newPi;
    
    return ReestimationResult_t(alphabeta2.logmodelcost);

}

HmmDataMatrix_t HiddenMarkovModel::getGammaFromViterbiPath(const ViterbiPath_t & path,const size_t numStates,const size_t numObs) const {
    HmmDataMatrix_t gamma = getZeroedMatrix(numStates, numObs);

    for (int t = 0; t < numObs; t++) {
        gamma[path[t]][t] = 1;
    }

    return gamma;
}

HmmDataMatrix_t HiddenMarkovModel::reestimateAFromViterbiPath(const ViterbiPath_t & path, const HmmDataMatrix_t & meas,size_t numObs,size_t numStates,const HmmDataMatrix_t & originalA) const {
    HmmDataMatrix_t A = getZeroedMatrix(numStates, numStates);
    
    int t,j,i;
    
    for (t = 1; t < numObs; t++) {
        const int32_t fromidx = path[t-1];
        const int32_t toidx = path[t];
        A[fromidx][toidx] += 1.0;
    }
    
    for (j = 0; j < numStates; j++) {
        HmmFloat_t sum = 0.0;
        for (i = 0; i < numStates; i++) {
            sum += A[j][i];
        }
        
        if (sum > EPSILON) {
            for (i = 0; i < numStates; i++) {
                A[j][i] /= sum;
            }
        }
        
    }
    
    for (j = 0; j < numStates; j++) {
        for (i = 0; i < numStates; i++) {
            
            if (originalA[j][i] > EPSILON) {
                if (A[j][i] <= MIN_VALUE_FOR_A) {
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
    
    ModelVec_t newModels = reestimateFromGamma(gamma,meas);
    
    //otherwise.... full steam ahead
    _models.clear();
    
    for (ModelVec_t::iterator it = newModels.begin(); it != newModels.end(); it++) {
        addModelForState((*it).get()->clone(false));
    }

    
    _A = reestimateAFromViterbiPath(res.path,meas,numObs,_numStates,_A);
    
    return ReestimationResult_t(res.cost);
}

static bool isGoodStateTransitionMatrix(const HmmDataMatrix_t & A) {
    HmmDataVec_t rowsums;
    rowsums.resize(A.size());
    
    memset(rowsums.data(),0,sizeof(HmmFloat_t) * rowsums.size());
    
    for (int i = 0; i < A.size(); i++) {
        for (int j = 0; j < A[i].size(); j++) {
            rowsums[i] += A[i][j];
        }
    }
    
    for (int i = 0; i < A.size(); i++) {
        if (rowsums[i] < 0.99) {
            return false;
        }
    }

    return true;
    
}

bool HiddenMarkovModel::reestimateViterbiSplitState(uint32_t s1, uint32_t s2,const ViterbiPath_t & originalViterbi,const HmmDataMatrix_t & meas) {
    
    uint32_t ti,j,i;
    uint32_t iter;
    bool worked = true;
    
    HmmDataMatrix_t newA;
    
    const size_t numObs = meas[0].size();

    HmmDataMatrix_t logA = _A; //copy
    
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
       // std::cout << "split state " << s1 + 1 << " of " << _numStates - 1 << " failed because no obs belong to this state" << std::endl;
        return false;
    }
    
    for (iter = 0; iter < NUM_SPLIT_STATE_VITERBI_ITERATIONS; iter++) {
        
        //get logbmap
        HmmDataMatrix_t splitlogbmap;
        splitlogbmap.resize(2);
        
        splitlogbmap[0] = _models[s1]->getLogOfPdf(meas);
        splitlogbmap[1] = _models[s2]->getLogOfPdf(meas);

        
        ViterbiPathMatrix_t vindices = getZeroedPathMatrix(2, myTimeIndices.size());
        HmmDataMatrix_t phi = getLogZeroedMatrix(2, myTimeIndices.size());
        UIntSet_t restartIndices;
        restartIndices.reserve(myTimeIndices.size());
        int32_t previdx = -1;

        for (ti = 0; ti < myTimeIndices.size(); ti++) {
            
            const int32_t tidx = myTimeIndices[ti];
            
            if (tidx == 0) {
                phi[0][0] = elnproduct(splitlogbmap[0][0], eln(_pi[s1]));
                phi[1][0] = elnproduct(splitlogbmap[1][0], eln(_pi[s2]));
            }
            else {
            
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
            }
            
            previdx = tidx;
        }
        
        
        //copy out the measurement indices that belong to this split states
        //i.e. the time indices from the viterbi path
        
        HmmDataMatrix_t measurementSubset;
        measurementSubset.resize(meas.size());

        for (int irow = 0; irow < measurementSubset.size(); irow++) {
            const HmmDataVec_t & row = meas[irow];
            measurementSubset[irow].resize(myTimeIndices.size());
            
            for (int t = 0; t < myTimeIndices.size(); t++) {
                measurementSubset[irow][t] = row[myTimeIndices[t]];
            }
        }
        
        
        
        const ViterbiDecodeResult_t res = decodePathAndGetCost(0, vindices, phi,restartIndices);
        
        const HmmDataVec_t fracs = getFractionInEachState(2, res.path);
        (void)fracs;
        
        const HmmDataMatrix_t gamma = getGammaFromViterbiPath(res.path,2,myTimeIndices.size());

        _models[s1] = _models[s1]->reestimate(gamma[0], measurementSubset);
        _models[s2] = _models[s2]->reestimate(gamma[1], measurementSubset);
        
        
        HmmDataMatrix_t originalA = getZeroedMatrix(2, 2);
        
        for (j = 0; j < 2; j++) {
            for (i = 0; i < 2; i++) {
                originalA[j][i] = eexp(splitLogA[j][i]);
            }
        }
        
        
        newA = reestimateAFromViterbiPath(res.path, measurementSubset, myTimeIndices.size(),2,originalA);
        
        if (!isGoodStateTransitionMatrix(newA)) {
            
            worked = false;
            break;
        }
        
        for (j = 0; j < 2; j++) {
            for (i = 0; i < 2; i++) {
                splitLogA[j][i] = eln(newA[j][i]);
            }
        }
        
        
    }
    
    _A[s1][s1] = eexp(splitLogA[0][0]);
    _A[s1][s2] = eexp(splitLogA[0][1]);
    _A[s2][s1] = eexp(splitLogA[1][0]);
    _A[s2][s2] = eexp(splitLogA[1][1]);
    
    return worked;
    
}

HmmFloat_t HiddenMarkovModel::getModelCost(const HmmDataMatrix_t & meas) const {
    const size_t numObs = meas[0].size();

    const HmmDataMatrix_t logbmap = getLogBMap(_models,meas);
    
    const AlphaBetaResult_t res = getAlphaAndBeta(numObs, _pi, logbmap, _A);
    
    return -res.logmodelcost;
}

uint32_t HiddenMarkovModel::getNumberOfFreeParams() const {
    uint32_t sum = 0.0;
    for (ModelVec_t::const_iterator it = _models.begin(); it != _models.end(); it++) {
        sum = (*it)->getNumberOfFreeParams();
    }
    
    return sum;
}


static HmmFloat_t train (HiddenMarkovModel * hmm,const HmmDataMatrix_t & meas) {
    ReestimationResult_t res;
    const HmmFloat_t bicSecondTerm = hmm->getNumberOfFreeParams() * log(meas[0].size());
    HmmFloat_t bestScore = -INFINITY;
    bool stopTrainingIfReestimationDoesNotImprove = false;
    
#ifdef QUIT_TRAINING_IF_NO_IMPROVEMENT
    stopTrainingIfReestimationDoesNotImprove = true;
#endif
    
    for (int i = 0; i < NUM_REESTIMATIONS_FOR_INTIAL_GUESS_PER_ITER; i++) {
        res = hmm->reestimateViterbi(meas);
        std::cout << res.getLogLikelihood() << std::endl;
    }
    
    for (int i = 0; i < MAX_NUM_REESTIMATIONS_PER_ITER; i++) {
        bool quitIfBad = stopTrainingIfReestimationDoesNotImprove;
        
        if (i < MIN_NUM_REESTIMATIONS) {
            quitIfBad = false;
        }
        
        res = hmm->reestimate(meas,quitIfBad);
        
        if (!res.isValid()) {
            break;
        }
        
        bestScore = 2 * res.getLogLikelihood() - bicSecondTerm;

        std::cout << res.getLogLikelihood() << std::endl;
    }
    
    return bestScore;
}



void  HiddenMarkovModel::enlargeWithVSTACS(const HmmDataMatrix_t & meas, uint32_t numToGrow) {
    ReestimationResult_t res;
    HmmFloat_t lastBIC = -INFINITY;
    
    uint32_t numStates = _numStates;
    HiddenMarkovModel * best = new HiddenMarkovModel(*this); //init
    
    for (uint32_t iter = 0; iter < numToGrow; iter++) {
        HmmVec_t hmms;
        UIntVec_t modelidx;
        HmmDataVec_t costs;


        std::cout << "BEGIN GROWING STATE " << numStates << std::endl;
     
        train(best,meas);
        
        const ViterbiDecodeResult_t res = best->decode(meas);
        
        const HmmDataVec_t fractionInEachState = getFractionInEachState(numStates,res.path);
        std::cout << fractionInEachState << std::endl;

        for (uint32_t iState = 0; iState < numStates; iState++) {
            if (fractionInEachState[iState] > MIN_FRAC_IN_STATE_TO_SPLIT / (HmmFloat_t)numStates) {
                HiddenMarkovModel * newSplitModel = best->splitState(iState);
                
                hmms.push_back(newSplitModel);
                modelidx.push_back(iState);
            }
        }
        
        
        costs.resize(hmms.size());

        
        
#ifdef USE_THREADPOOL
        FutureCostVec_t newevals;
        
        {
            //destructor of threadpool joins all threads
            ThreadPool pool(THREAD_POOL_SIZE);
            
            for (int32_t iModel = 0; iModel < hmms.size(); iModel++) {
                newevals.emplace_back(pool.enqueue([numStates,iModel,&hmms,&meas,&res,&modelidx] {
                    HmmFloat_t score = -INFINITY;

                    if (hmms[iModel]->reestimateViterbiSplitState(modelidx[iModel], numStates, res.path, meas)) {
                        const ViterbiDecodeResult_t res2 = hmms[iModel]->decode(meas);
                        score = res2.bic;
                    }
                    
                    return std::make_pair(iModel,score);
                
                }));
            }
        }
        
        //go get results and place in models vec
        for(auto && result : newevals) {
            StateIdxCostPair_t v = result.get();
            costs[v.first] = v.second;
        }
        
#else

        
        for (uint32_t iModel = 0; iModel < hmms.size(); iModel++) {
            
            if (hmms[iModel]->reestimateViterbiSplitState(modelidx[iModel], numStates, res.path, meas)) {
                const ViterbiDecodeResult_t res = hmms[iModel]->decode(meas);
                
                costs[iModel] = res.bic;
            }
            else {
                costs[iModel] = -INFINITY;
            }
        }
#endif
        std::cout << costs << std::endl;
        
        const uint32_t bestidx = getArgMaxInVec(costs);
        
        
        std::cout << "picked split of state " << bestidx << " BIC was " << costs[bestidx] << std::endl;
        
       // delete best; //replace with new
        best = new HiddenMarkovModel(*hmms[bestidx]);
        
        //delete the models that were split
        for (HmmVec_t::iterator itHmm = hmms.begin(); itHmm != hmms.end(); itHmm++) {
          //  delete *itHmm;
        }
        
        hmms.clear();
       
#ifdef QUIT_ENLARGING_IF_NO_IMRPOVEMENT_SEEN
        if (costs[bestidx] < lastBIC + lastBIC*1e-1) {
            std::cout << "EXITING, NO IMPROVEMENT SEEN" << std::endl;
            break;
        }
#endif
        
        
        lastBIC = costs[bestidx];
        

        
        numStates++;
    }
    
    
    std::cout << "BEST BIC: " << lastBIC << std::endl;

    //train(best,meas);
    
    /*
    for (int i = 0; i < NUM_FINAL_ITERTIONS; i++) {
        res = best->reestimate(meas); //converge to something with viterbi training
        std::cout << "FINAL REESTIMATION " << res.getLogLikelihood() << std::endl;
    }
     */
    
    
    *this = *best;
    
    delete best;
    
    
}


void  HiddenMarkovModel::enlargeRandomly(const HmmDataMatrix_t & meas, uint32_t numToGrow) {

    int32_t numStates = _numStates;
    HmmVec_t hmms;
    HmmDataVec_t scores;
    HmmFloat_t lastScore = -INFINITY;
    bool worked = true;
    
    
    HiddenMarkovModel * best = new HiddenMarkovModel(*this);
    
    for (int iter = 0; iter < numToGrow; iter++) {
        std::cout << "Beginning iteration " << iter + 1 << " of " << _numStates + numToGrow <<std::endl;
        scores.clear();
        
        //split each state
        for (int imodel = 0; imodel < numStates; imodel++) {
            hmms.push_back(best->splitState(imodel));
        }
        
        //train each state
        for (int imodel = 0; imodel < numStates; imodel++) {
            std::cout << "Training model " << imodel + 1 << " of " << numStates << std::endl;
            scores.push_back(train(hmms[imodel],meas));
        }
        
        //get best one
        
        std::cout << "SCORES: " << scores << std::endl;
        const int bestIdx = getArgMaxInVec(scores);
        const HmmFloat_t bestScore = scores[bestIdx];
        
        if (lastScore < bestScore) {
            
            delete best;
            best = hmms[bestIdx];
            
            std::cout << "picked model " << bestIdx + 1 << " in group " << best->_groups[numStates - 1] << std::endl;
            std::cout << "BEST SCORE: " <<  scores[bestIdx] << std::endl;

        }
        else {
            std::cout << "TERMINATING BECAUSE MODEL DID NOT IMPROVE" << std::endl;
            worked = false;
        }
        
        lastScore = bestScore;
        
        
        
        for (HmmVec_t::iterator it = hmms.begin(); it != hmms.end(); it++) {
            if (*it != best) {
                delete *it;
            }
        }
        
        numStates++;
        
        hmms.clear();
        
        if (!worked) {
            break;
        }
        
    }
    
    *this = *best;
    
    delete best;
    
}


