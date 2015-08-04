#include "HiddenMarkovModel.h"
#include "HmmTypes.h"
#include "LogMath.h"
#include "ThreadPool.h"
#include <iostream>
#include "SerializationHelpers.h"
#include "MatrixHelpers.h"
#include <assert.h>
#include <string.h>
#include "RandomHelpers.h"

#define MIN_VALUE_FOR_A (1e-3)
#define MAX_VALUE_FOR_A (1.0 - MIN_VALUE_FOR_A)

#define SPLIT_A_PERTURBATION_MAX (0.02)

#define NUM_REESTIMATIONS_FOR_INTIAL_GUESS_PER_ITER (0)
#define MAX_NUM_REESTIMATIONS_PER_ITER (100)
#define MIN_NUM_REESTIMATIONS (1)

#define NUM_SPLIT_STATE_VITERBI_ITERATIONS (20)

#define THRESHOLD_FOR_REMOVING_STATE (0.0001)
#define NUM_SPLITS_PER_STATE (10)
#define DAMPING_FACTOR (0.02)

#define MIN_VALUE_FOR_SELF_TERM (0.01)

#define NUM_BAD_COUNTS_TO_EXIT (2)

#define THREAD_POOL_SIZE (8)
#define USE_THREADPOOL
#define QUIT_TRAINING_IF_NO_IMPROVEMENT
#define QUIT_ENLARGING_IF_NO_IMRPOVEMENT_SEEN

typedef std::pair<int32_t,HmmPdfInterfaceSharedPtr_t> StateIdxModelPair_t;
typedef std::pair<int32_t,HmmDataVec_t> StateIdxPdfEvalPair_t;
typedef std::pair<int32_t,HmmFloat_t> StateIdxCostPair_t;

typedef std::vector<std::future<StateIdxModelPair_t>> FutureModelVec_t;
typedef std::vector<std::future<StateIdxPdfEvalPair_t>> FuturePdfEvalVec_t;
typedef std::vector<std::future<StateIdxCostPair_t>> FutureCostVec_t;


typedef std::vector<HmmSharedPtr_t> HmmVec_t;

template <typename T>
UIntVec_t sort_indexes(const std::vector<T> &v) {
    
    // initialize original index locations
    UIntVec_t idx(v.size());
    for (size_t i = 0; i != idx.size(); ++i) idx[i] = i;
    
    // sort indexes based on comparing values in v
    std::sort(idx.begin(), idx.end(),
              [&v](uint32_t i1, uint32_t i2)
              {return v[i1] < v[i2];}
              );
    
    return idx;
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

HiddenMarkovModel::HiddenMarkovModel(const HmmDataMatrix_t & A, SaveStateInterface * stateSaver)
:_A(A)
,_stateSaver(stateSaver) {
    
    _numStates = A.size();
    _pi = getUniformVec(_numStates);

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
    _stateSaver = hmm._stateSaver;
    
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
    
    std::stringstream ss;
    ss <<  "\"params\": {\"natural_light_filter_start_hour\": 16, \"on_bed_states\": [], \"users\": \"\", \"num_model_params\":" << getNumberOfFreeParams() << ", \"natural_light_filter_stop_hour\": 4, \"pill_magnitude_disturbance_threshold_lsb\": 15000, \"sleep_states\": [], \"enable_interval_search\": true, \"model_name\": \"foobars\", \"audio_disturbance_threshold_db\": 70.0 , \"meas_period_minutes\" : 5}";
    
    return makeObj(makeKeyValue("default",makeObj(A + "," + models + "," + pi + "," + ss.str())));
}


void HiddenMarkovModel::addModelForState(HmmPdfInterfaceSharedPtr_t model) {
    _models.push_back(model);
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
    return HmmHelpers::getAlphaAndBeta(numObs, pi, logbmap, A, _numStates);
}

Hmm3DMatrix_t HiddenMarkovModel::getLogXi(const AlphaBetaResult_t & alphabeta,const HmmDataMatrix_t & logbmap,size_t numObs) const {
    return HmmHelpers::getLogXi(alphabeta, logbmap, numObs, _numStates);
}

HmmDataMatrix_t HiddenMarkovModel::getLogGamma(const AlphaBetaResult_t & alphabeta,size_t numObs) const {
    return HmmHelpers::getLogGamma(alphabeta, numObs, _numStates);
}

HmmDataMatrix_t HiddenMarkovModel::reestimateA(const Hmm3DMatrix_t & logxi, const HmmDataMatrix_t & loggamma,const size_t numObs,const HmmFloat_t damping, const HmmFloat_t minValueForA) const {
    
    return HmmHelpers::reestimateA(_A, logxi, loggamma, numObs, DAMPING_FACTOR, MIN_VALUE_FOR_A,_numStates);
}

static ViterbiPath_t decodePath(int32_t startidx,const ViterbiPathMatrix_t & paths) {
    size_t len = paths[0].size();
    
    
    ViterbiPath_t path;
    path.resize(len);
    
    path[len-1] = startidx;
    for(int i = len - 2; i >= 0; i--) {
        path[i] = paths[path[i+1]][i];
    }
    
    
    return path;
}

ViterbiDecodeResult_t HiddenMarkovModel::decodePathAndGetCost(int32_t startidx,const ViterbiPathMatrix_t & paths,const HmmDataMatrix_t & phi) const  {

    const size_t len = paths[0].size();

    
    //get viterbi path
    ViterbiPath_t path = decodePath(startidx,paths);
    
    //compute cost stuff
    const HmmFloat_t cost = phi[path[len-1]][len-1];
    
    //really -bic

    const HmmFloat_t bic = 2*cost - this->getNumberOfFreeParams() * log(len);

    return ViterbiDecodeResult_t(path,cost,bic);
}

HmmSharedPtr_t HiddenMarkovModel::deleteStates(UIntSet_t statesToDelete) const {
    const uint32_t numNewStates = _numStates - statesToDelete.size();
    
    HmmDataMatrix_t A = getZeroedMatrix(numNewStates,numNewStates);
    int row = 0;
    for (int j = 0; j < _numStates; j++) {
        int col = 0;
        
        if (statesToDelete.find(j) != statesToDelete.end()) {
            continue;
        }
        
        for (int i = 0; i < _numStates; i++) {
            if (statesToDelete.find(i) != statesToDelete.end()) {
                continue;
            }
            
            A[row][col] = _A[j][i];
            
            col++;
        }
        
        row++;
    }
    
    HiddenMarkovModel * newModel = new HiddenMarkovModel(A,_stateSaver);
    
    
    
    for (int j = 0; j < _numStates; j++) {
        
        if (statesToDelete.find(j) != statesToDelete.end()) {
            continue;
        }
        
        newModel->addModelForState(_models[j]->clone(false));
    }
    
    return HmmSharedPtr_t(newModel);
    
}


HmmSharedPtr_t HiddenMarkovModel::splitState(uint32_t stateToSplit,bool perturbSelfTerm,bool perturbMeasurements) const {
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
        //columns... so transitioning from any state to the states that are being split
        //so these values are the original transition probabilities divided by 2
        const int idx = splitIndices[i];
        
        //s' --> si
        for (j = 0; j < _numStates; j++) {
            if (j != splitIndices[0] && j != splitIndices[1]) {
                splitA[j][idx] = 0.5 * _A[j][stateToSplit];
            }
        }
    }
    
    for (i = 0; i < 2; i++) {
        //rows of the split states... so transitioning from split state to any other state
        //keep them the same as the original state that was split
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
    //transition probabilties between the split states
    splitA[splitIndices[0]][splitIndices[0]] = _A[stateToSplit][stateToSplit];
    splitA[splitIndices[0]][splitIndices[1]] = 0.01; //0.5 * _A[stateToSplit][stateToSplit];
    splitA[splitIndices[1]][splitIndices[0]] = 0.01; //0.5 * _A[stateToSplit][stateToSplit];
    splitA[splitIndices[1]][splitIndices[1]] = _A[stateToSplit][stateToSplit];

    
    std::stringstream ss;
    ss << "splitA - " << stateToSplit;
    //printMat(ss.str(), splitA);
    
    if (perturbSelfTerm) {
        HmmFloat_t a0 = splitA[splitIndices[0]][splitIndices[0]];
        HmmFloat_t a1 = splitA[splitIndices[1]][splitIndices[1]];
        
        HmmFloat_t T1 = 1.0 / (1.0 - a0);
        HmmFloat_t T2 = 1.0 / (1.0 - a1);
        
        if (T1 == INFINITY || isnan(T1) || T2 == INFINITY || isnan(T2) ) {
            std::cerr << "bolloxed up self term in split transition matrix " << std::endl;
        }
        else {
            
            T1 *= 1.0;
            T2 *= (1.0 + getRandomFloat()) * 2; //between 0 and 2

            a0 = 1.0 - 1.0 / T1;
            a1 = 1.0 - 1.0 / T2;
        }
        
        splitA[splitIndices[0]][splitIndices[0]] = a0;
        splitA[splitIndices[1]][splitIndices[1]] = a1;

        HmmDataVec_t & row0 = splitA[splitIndices[0]];
        HmmDataVec_t & row1 = splitA[splitIndices[1]];
        HmmFloat_t sum0 = 0;
        HmmFloat_t sum1 = 0;
        for (j = 0; j < _numStates + 1; j++) {
            sum0 += row0[j];
            sum1 += row1[j];
        }
        
        for (j = 0; j < _numStates + 1; j++) {
            row0[j] /= sum0;
            row1[j] /= sum1;
        }

    }
    

    //create the new split model
    
    HiddenMarkovModel * splitModel = new HiddenMarkovModel(splitA,_stateSaver);
    
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
    splitModel->addModelForState(modelToSplit->clone(perturbMeasurements));
    
    return HmmSharedPtr_t(splitModel);
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
    
    const ViterbiDecodeResult_t result = decodePathAndGetCost(0, vindices, phi);
    
    
    return result;
    
}

ModelVec_t HiddenMarkovModel::reestimateFromGamma(const HmmDataMatrix_t & gamma, const HmmDataMatrix_t & meas, const HmmFloat_t eta) const {
    
    ModelVec_t updatedModels;
    
#ifdef USE_THREADPOOL
    const ModelVec_t localModels = _models; //copies all the pointers
    FutureModelVec_t newmodels;
    
    {
        //destructor of threadpool joins all threads
        ThreadPool pool(THREAD_POOL_SIZE);
        
        for (int32_t iState = 0; iState < _numStates; iState++) {
            newmodels.emplace_back(
                                   pool.enqueue([iState,&gamma,&meas,&localModels,eta] {
                return std::make_pair(iState,localModels[iState]->reestimate(gamma[iState], meas,eta));
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
            
            HmmPdfInterfaceSharedPtr_t newModel = _models[iState]->reestimate(gammaForThisState, meas,eta);
            
            updatedModels.push_back(newModel);
        }
        
    }
    
#endif
    
    return updatedModels;
}

ReestimationResult_t HiddenMarkovModel::reestimate(const HmmDataMatrix_t & meas,bool dontReestimateIfScoreDidNotImprove, const HmmFloat_t minValueForA) {
    if (meas.empty()) {
        return ReestimationResult_t();
    }
    
    const size_t numObs = meas[0].size();
    
    const HmmDataMatrix_t logbmap = getLogBMap(_models,meas);
    
    const AlphaBetaResult_t alphabeta = getAlphaAndBeta(numObs, _pi, logbmap, _A);
    
    const Hmm3DMatrix_t logxi = getLogXi(alphabeta,logbmap,numObs);
    
    const HmmDataMatrix_t loggamma = getLogGamma(alphabeta,numObs);
    
    const HmmDataMatrix_t newA = reestimateA(logxi, loggamma, numObs,DAMPING_FACTOR,minValueForA);
    
    
    HmmDataMatrix_t gamma = getEEXPofMatrix(loggamma);
    
    HmmDataVec_t newPi = getZeroedVec(_numStates);
    
    for (int i = 0; i < _numStates; i++) {
        newPi[i] = gamma[i][0];
    }
    
    
    ModelVec_t newModels = reestimateFromGamma(gamma,meas,DAMPING_FACTOR);
    
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
        HmmPdfInterfaceSharedPtr_t theClone = (*it)->clone(false);
        addModelForState(theClone);
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
                
                if (A[j][i] > MAX_VALUE_FOR_A) {
                    A[j][i] = MAX_VALUE_FOR_A;
                }
            }
            
        }
    }
    
    return A;
    
}


ReestimationResult_t HiddenMarkovModel::reestimateViterbi(const HmmDataMatrix_t & meas) {
    
    const size_t numObs = meas[0].size();
    
    const ViterbiDecodeResult_t res = this->decode(meas);
    
    const HmmDataMatrix_t gamma = getGammaFromViterbiPath(res.getPath(),_numStates,numObs);
    
    ModelVec_t newModels = reestimateFromGamma(gamma,meas,DAMPING_FACTOR);
    
    //otherwise.... full steam ahead
    _models.clear();
    
    for (ModelVec_t::iterator it = newModels.begin(); it != newModels.end(); it++) {
        addModelForState((*it).get()->clone(false));
    }

    
    _A = reestimateAFromViterbiPath(res.getPath(),meas,numObs,_numStates,_A);
    
    return ReestimationResult_t(res.getCost());
}

/*
static void getMeanObsFromSegments(const StateSegmentVec_t & segs, const HmmDataMatrix_t & meas) {
    for (StateSegmentVec_t::const_iterator it = segs.begin(); it != segs.end(); it++) {
        const StateSegment_t & seg = *it;
        
        HmmDataVec_t mean = getZeroedVec(meas.size());
        const int len = seg.timeIndices.second - seg.timeIndices.first + 1;
        for (int t = seg.timeIndices.first; t <= seg.timeIndices.second; t++) {
            for (int i = 0; i < meas.size(); i++) {
                mean[i] += meas[i][t];
            }
        }
        
        for (int i = 0; i < meas.size(); i++) {
            mean[i] /= len;
        }
    
        
        int foo = 3;
        foo++;
    }
    
}
*/

bool HiddenMarkovModel::reestimateViterbiSplitState(uint32_t s1, uint32_t s2,const ViterbiPath_t & originalViterbi,const HmmDataMatrix_t & meas, bool reestimateMeas) {
    
    //s1 is always the original state that was split
    //s2 is always the last state, with index = numstates (zero-based index)
    uint32_t j,i,t;
    uint32_t iter;
    bool worked = true;
    const uint32_t totalNumObs = meas[0].size();
    HmmDataMatrix_t newA;
    
    
    
    //get counts from full path before split
    HmmDataMatrix_t countmat = getZeroedMatrix(_numStates, _numStates);
    for (t = 1; t < totalNumObs; t++) {
        const int32_t fromidx = originalViterbi[t-1];
        const int32_t toidx = originalViterbi[t];
        countmat[fromidx][toidx] += 1.0;
    }
    
   
    
    //find out which segments belong to state == s1, and where they transitioned from
    const StateSegmentVec_t segs = getStateInfo(originalViterbi,s1);
    
    typedef std::pair<StateSegment_t,ViterbiPath_t> SegPath_t;
    typedef std::vector<SegPath_t> SegPathVec_t;
    
    for (iter = 0; iter < NUM_SPLIT_STATE_VITERBI_ITERATIONS; iter++) {
        //get incoming transition terms
        HmmDataMatrix_t logA = _A; //copy
        
        for (j = 0; j < _numStates; j++) {
            for (i = 0; i < _numStates; i++) {
                logA[j][i] = eln(logA[j][i]);
            }
        }
        
        HmmDataMatrix_t logAIncoming = getZeroedMatrix(2, _numStates);
        
        for (i = 0; i < _numStates; i++) {
            logAIncoming[0][i] = logA[i][s1];
            logAIncoming[1][i] = logA[i][s2];
        }
        
        //get outgoing transition terms
        HmmDataMatrix_t logAOutgoing = getZeroedMatrix(2, _numStates);
        
        for (i = 0; i < _numStates; i++) {
            logAOutgoing[0][i] = logA[s1][i];
            logAOutgoing[1][i] = logA[s2][i];
        }

        
        //get logbmap
        HmmDataMatrix_t splitlogbmap;
        splitlogbmap.resize(2);
        
        splitlogbmap[0] = _models[s1]->getLogOfPdf(meas);
        splitlogbmap[1] = _models[s2]->getLogOfPdf(meas);
        
        uint32_t totalLength = 0;
        
        SegPathVec_t segmentsWithPath;

        //calculate the little phi batches
        for (StateSegmentVec_t::const_iterator it = segs.begin(); it != segs.end(); it++) {
            const StateSegment_t & seg = *it;
            const uint32_t seglength = seg.timeIndices.second - seg.timeIndices.first + 1;
            //std::cout << seglength << ",";
            totalLength += seglength;
            
            HmmDataMatrix_t phi = getZeroedMatrix(2, seglength);
            ViterbiPathMatrix_t vindices = getZeroedPathMatrix(2, seglength);

            
            for (t = seg.timeIndices.first; t <= seg.timeIndices.second; t++) {
                const int idx = t - seg.timeIndices.first; //0, 1, 2, 3, ... N
                
                if (t == 0) {
                    //start, and at t == 0
                    phi[0][idx] = elnproduct(splitlogbmap[0][0], eln(_pi[s1]));
                    phi[1][idx] = elnproduct(splitlogbmap[1][0], eln(_pi[s2]));
                    
                    vindices[0][idx] = 0;
                    vindices[1][idx] = 1;

                }
                else if (idx == 0) {
                    //all other starts
                    HmmDataVec_t costs;
                    costs.resize(2);
                    
                    for (i = 0; i < 2; i++) {
                        const HmmFloat_t obscost = splitlogbmap[i][t];
                        const HmmFloat_t transitionInCost = logAIncoming[i][seg.fromAndToStates.first];

                        phi[i][idx] = elnproduct(transitionInCost, obscost);
                    }
                    
                    vindices[0][idx] = 0;
                    vindices[1][idx] = 1;
                }
                else {
                    //not a start
                    
                    HmmDataVec_t costs;
                    costs.resize(2);
                    
                    const HmmFloat_t obscost1 = splitlogbmap[0][t];
                    const HmmFloat_t obscost2 = splitlogbmap[1][t];
                    
                    
                    const HmmFloat_t transitionInCostS1S1 = elnproduct(phi[0][idx - 1], logAIncoming[0][s1]);
                    const HmmFloat_t transitionInCostS2S1 = elnproduct(phi[1][idx - 1], logAIncoming[0][s2]);
                    const HmmFloat_t transitionInCostS1S2 = elnproduct(phi[0][idx - 1], logAIncoming[1][s1]);
                    const HmmFloat_t transitionInCostS2S2 = elnproduct(phi[1][idx - 1], logAIncoming[1][s2]);
                    
                    //a failed experiment, ignore this
                    //const HmmFloat_t transitionInCostS2S1 = -INFINITY;
                    //const HmmFloat_t transitionInCostS1S2 = -INFINITY;

                    
                    costs[0] = elnproduct(transitionInCostS1S1, obscost1);
                    costs[1] = elnproduct(transitionInCostS2S1, obscost1);
                    
                    const uint32_t maxidx1 = getArgMaxInVec(costs);
                    
                    phi[0][idx] = costs[maxidx1];
                    vindices[0][idx] = maxidx1;
                    
                    
                    costs[0] = elnproduct(transitionInCostS1S2, obscost2);
                    costs[1] = elnproduct(transitionInCostS2S2, obscost2);
                    
                    const uint32_t maxidx2 = getArgMaxInVec(costs);
                    
                    phi[1][idx] = costs[maxidx2];
                    vindices[1][idx] = maxidx2;
                
                    
                }
                
            }
            
            
            //now with my little phi and vindices, I will do the decode!
            uint32_t endingIndx = 0;
            if (phi[1][seglength - 1] > phi[0][seglength - 1]) {
                endingIndx = 1;
            }
            const ViterbiPath_t path = decodePath(endingIndx, vindices);

            //save gamma/segment combo off
            segmentsWithPath.push_back(std::make_pair(seg,path));
            
        }
        
        //std::cout << std::endl;

        
        //reestimate obs, incoming, and outgoing
        //first, assemble the measurements and gammas into one glorious whole
        HmmDataMatrix_t gamma = getZeroedMatrix(2, totalLength);
        HmmDataMatrix_t meas2 = getZeroedMatrix(meas.size(), totalLength);
       
        uint32_t pos = 0;
        
        //concatenate the gammas and measurements
        for (SegPathVec_t::const_iterator it = segmentsWithPath.begin(); it != segmentsWithPath.end(); it++) {
        
            const StateSegment_t & seg = (*it).first;
            const ViterbiPath_t & path = (*it).second;
            const uint32_t seglength = seg.timeIndices.second - seg.timeIndices.first + 1;
            const HmmDataMatrix_t subgamma = getGammaFromViterbiPath(path,2,seglength);

            //copy gamma and meas
            for (i = 0; i < seglength; i++) {
                gamma[0][pos + i] = subgamma[0][i];
                gamma[1][pos + i] = subgamma[1][i];
                
                for (j = 0; j < meas.size(); j++) {
                    meas2[j][pos + i] = meas[j][seg.timeIndices.first + i];
                }
            }

            pos += seglength;
        }
        
        //now reestimate obs model params
        if (reestimateMeas) {
            HmmPdfInterfaceSharedPtr_t r1 = _models[s1]->reestimate(gamma[0], meas2,DAMPING_FACTOR);
            HmmPdfInterfaceSharedPtr_t r2 = _models[s2]->reestimate(gamma[1], meas2,DAMPING_FACTOR);
            
            _models[s1] = r1;
            _models[s2] = r2;
        }
        
        //count transitions
        HmmDataMatrix_t incomingCounts = getZeroedMatrix(2, _numStates);
        HmmDataMatrix_t outgoingCounts = getZeroedMatrix(2, _numStates);
        
        for (SegPathVec_t::const_iterator it = segmentsWithPath.begin(); it != segmentsWithPath.end(); it++) {
            
            const StateSegment_t & seg = (*it).first;
            const ViterbiPath_t & path = (*it).second;
            const uint32_t seglength = seg.timeIndices.second - seg.timeIndices.first + 1;
        
            const uint32_t startPathIdx = path[0];
            const uint32_t endPathIdx = path[seglength - 1];
            
            //increment incoming and outgoing to the other states
            incomingCounts[startPathIdx][seg.fromAndToStates.first] += 1.0;
            outgoingCounts[endPathIdx][seg.fromAndToStates.second] += 1.0;
            
            //track the incoming and outgoing between the split states
            for (i = 1; i < seglength; i++) {
                if (path[i] == 0 && path[i-1] == 0) {
                    incomingCounts[0][s1] += 1.0;
                    outgoingCounts[0][s1] += 1.0;
                }
                else if (path[i] == 1 && path[i-1] == 1) {
                    incomingCounts[1][s2] += 1.0;
                    outgoingCounts[1][s2] += 1.0;
                }
                else if (path[i] == 0 && path[i-1] == 1) {
                    incomingCounts[0][s2] += 1.0;
                    outgoingCounts[1][s1] += 1.0;
                }
                else if (path[i] == 1 && path[i-1] == 0) {
                    incomingCounts[1][s1] += 1.0;
                    outgoingCounts[0][s2] += 1.0;
                }
            }
        }
        
        
        //merge with countmat
        HmmDataMatrix_t counts = countmat;
        
        for (i = 0; i < _numStates; i++) {
            counts[s1][i] = outgoingCounts[0][i];
            counts[s2][i] = outgoingCounts[1][i];
            
            counts[i][s1] = incomingCounts[0][i];
            counts[i][s2] = incomingCounts[1][i];
        }
       
        //compute rowsums and normalize
        for (j = 0; j < _numStates; j++) {
            HmmFloat_t sum = 0.0;
            for (i = 0; i < _numStates; i++) {
                sum += counts[j][i];
            }
            
            if (sum < EPSILON) {
                //no counts in the split state, so this was just a waste of time
                if (j == s2) {
                    return false;
                }
                
                continue;
            }
            
            for (i = 0; i < _numStates; i++) {
                counts[j][i] /= sum;
                
                //if (j == s1 || j == s2) {
                    if (counts[j][i] < MIN_VALUE_FOR_A) {
                        counts[j][i] = MIN_VALUE_FOR_A;
                    }
                //}
            }
        }
        
        for (j = 0; j < _numStates; j++) {
            for (i = 0; i < _numStates; i++) {
                _A[j][i] += (counts[j][i] - _A[j][i]) * DAMPING_FACTOR;
            }
        }
    }
    
    /*
    if (_A[s2][s2] < MIN_SELF_TERM_FOR_SPLIT_STATE) {
        worked = false;
    }
    else {
    }
    
    
    std::cout << "state " << s2 << " self-term: " << _A[s2][s2] << ", outgoing: " << _A[s2] << std::endl;
*/
    /*
    std::cout << this->serializeToJson() << std::endl;
    std::cout << std::endl;
    std::cout << std::endl;
*/
    
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
        sum += (*it)->getNumberOfFreeParams();
    }
    
    return sum;
}


static HmmFloat_t train(HmmSharedPtr_t hmm,const HmmDataMatrix_t & meas,const HmmFloat_t minValueForA = MIN_VALUE_FOR_A, bool forceTraining = false,bool printstuff = true) {
    ReestimationResult_t res;
    const HmmFloat_t bicSecondTerm = hmm->getNumberOfFreeParams() * log(meas[0].size());
    HmmFloat_t bestScore = -INFINITY;
    bool stopTrainingIfReestimationDoesNotImprove = false;
    
#ifdef QUIT_TRAINING_IF_NO_IMPROVEMENT
    stopTrainingIfReestimationDoesNotImprove = true;
#endif
    
    if (forceTraining) {
        stopTrainingIfReestimationDoesNotImprove = false;
    }
    
    for (int i = 0; i < NUM_REESTIMATIONS_FOR_INTIAL_GUESS_PER_ITER; i++) {
        res = hmm->reestimateViterbi(meas);
        
    }
    
    for (int i = 0; i < MAX_NUM_REESTIMATIONS_PER_ITER; i++) {
        bool quitIfBad = stopTrainingIfReestimationDoesNotImprove;
        
        if (i < MIN_NUM_REESTIMATIONS) {
            quitIfBad = false;
        }
        
        res = hmm->reestimate(meas,quitIfBad,minValueForA);
        
        if (!res.isValid()) {
            break;
        }
        
        bestScore = 2 * res.getLogLikelihood() - bicSecondTerm;

        if (printstuff) {
            std::cout << bestScore << "," << std::flush;
        }
    }
    
    std::cout << std::endl;
    
    return bestScore;
}



void  HiddenMarkovModel::enlargeWithVSTACS(const HmmDataMatrix_t & meas, uint32_t numToGrow) {
    ReestimationResult_t res;
    ViterbiDecodeResult_t vres;
    HmmFloat_t lastBIC = -INFINITY;
    uint32_t badcount = 0 ;

    
    uint32_t numStates = _numStates;
    HmmSharedPtr_t best = HmmSharedPtr_t(new HiddenMarkovModel(*this)); //init
    
    for (uint32_t iter = 0; iter < numToGrow; iter++) {
        HmmVec_t hmms;
        UIntVec_t modelidx;
        UIntVec_t reestimateMeasVec;
        HmmDataVec_t costs;


        std::cout << "BEGIN GROWING, ITER = " << iter << ", NUMSTATES = " << numStates << std::endl;
     
        train(best,meas,MIN_VALUE_FOR_A,false,false);
        
        vres = best->decode(meas);
        
        const HmmDataVec_t fractionInEachState = getFractionInEachState(numStates,vres.getPath());

        
        //prune one if necessary
        const uint32_t origNumberStates = numStates;
        UIntSet_t statesToDelete;
        
        bool isDegenerate = false;
        //handle degenerate case where only 1 state is on the viterbi path (usually due to bad initialization)
        for (uint32_t iState = 0; iState < origNumberStates; iState++) {
            if (fractionInEachState[iState] > 0.9999) {
                isDegenerate = true;
                break;
            }
        }
        
        if (isDegenerate) {
            std::cout << "FAILING BECAUSE MODEL IS DEGENERATE (ONLY DECODES TO ONE STATE)" <<std::endl;
            break;
        }
        
        for (uint32_t iState = 0; iState < origNumberStates; iState++) {
            //did state get too concentrated?
            for (int i = 0; i < origNumberStates; i++) {
                if (best->_A[iState][i] > 1.0 - origNumberStates*MIN_VALUE_FOR_A) {
                    statesToDelete.insert(iState);
                }
            }
            
            //is self term too small?
            if (best->_A[iState][iState] < MIN_VALUE_FOR_SELF_TERM) {
                statesToDelete.insert(iState);
            }
            
            
            
            if (fractionInEachState[iState] < THRESHOLD_FOR_REMOVING_STATE) {
                statesToDelete.insert(iState);
            }
        }
        
        
        if (!statesToDelete.empty() && statesToDelete.size() < origNumberStates) {
            std::cout << "deleting states " << statesToDelete << std::endl;
            best = best->deleteStates(statesToDelete);
            numStates -= statesToDelete.size();
            
            //if you deleted, re-run viterbi
            vres = best->decode(meas);
        }
        
        
#ifdef QUIT_ENLARGING_IF_NO_IMRPOVEMENT_SEEN
        if (vres.getBIC() < lastBIC || vres.getBIC() == -INFINITY) {
            badcount++;
            std::cout << "no improvement..." << std::endl;
            if (badcount > NUM_BAD_COUNTS_TO_EXIT) {
                std::cout << "EXITING, NO IMPROVEMENT SEEN" << std::endl;
                break;
            }
        }
        else {
            badcount = 0;
        }
#endif
        
        lastBIC = vres.getBIC();
        
        if (_stateSaver) {
            _stateSaver->saveState(best->serializeToJson());
        }
        
        
        //splits
        for (uint32_t iState = 0; iState < numStates; iState++) {
            
            for (int isplit = 0; isplit < NUM_SPLITS_PER_STATE; isplit++) {
                HmmSharedPtr_t newSplitModel = best->splitState(iState,true,isplit != 0);
                
                hmms.push_back(newSplitModel);
                modelidx.push_back(iState);
                reestimateMeasVec.push_back(isplit != 0);
            }
        }
        
        
        costs.resize(hmms.size());

        ViterbiPath_t path = vres.getPath();
        
#ifdef USE_THREADPOOL
        FutureCostVec_t newevals;
        
        {
            //destructor of threadpool joins all threads
            ThreadPool pool(THREAD_POOL_SIZE);
            
            for (int32_t iModel = 0; iModel < hmms.size(); iModel++) {
                newevals.emplace_back(pool.enqueue([numStates,iModel,&hmms,&meas,&path,&modelidx,&reestimateMeasVec] {
                    HmmFloat_t score = -INFINITY;

                    if (hmms[iModel]->reestimateViterbiSplitState(modelidx[iModel], numStates, path, meas,reestimateMeasVec[iModel])) {
                        const ViterbiDecodeResult_t res2 = hmms[iModel]->decode(meas);
                        score = res2.getBIC();
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
            //std::cout << hmms[iModel]->serializeToJson() << std::endl;
            if (hmms[iModel]->reestimateViterbiSplitState(modelidx[iModel], numStates, path, meas,reestimateMeasVec[iModel])) {
                const ViterbiDecodeResult_t res = hmms[iModel]->decode(meas);
                
                costs[iModel] = res.getBIC();
            }
            else {
                costs[iModel] = -INFINITY;
            }
        }
#endif
        //std::cout << costs << std::endl;
        
        if (costs.empty()) {
            std::cout << "NO VIABLE SPLITS FOUND, EXITING." << std::endl;
            break;
        }
        
        const uint32_t bestidx = getArgMaxInVec(costs);
        
        
        
        std::cout << "picked split of state " <<  modelidx[bestidx] << " BIC was " << costs[bestidx] << std::endl;
        
        best = hmms[bestidx];
        
        hmms.clear();
        
        numStates++;
        
    }
    
    
    
    
    std::cout << "BEST BIC: " << lastBIC << std::endl;
    
    /*
    for (int i = 0; i < NUM_FINAL_ITERTIONS; i++) {
        res = best->reestimate(meas); //converge to something with viterbi training
        std::cout << "FINAL REESTIMATION " << res.getLogLikelihood() << std::endl;
    }
     
    
    ViterbiDecodeResult_t finalresult = best->decode(meas);
    
    std::cout << finalresult.getPath() << std::endl;
    */
    
    *this = *best;
    
}


void  HiddenMarkovModel::enlargeRandomly(const HmmDataMatrix_t & meas, uint32_t numToGrow) {

    int32_t numStates = _numStates;
    HmmVec_t hmms;
    HmmDataVec_t scores;
    HmmFloat_t lastScore = -INFINITY;
    bool worked = true;
    
    
    HmmSharedPtr_t best = HmmSharedPtr_t(new HiddenMarkovModel(*this));
    
    for (int iter = 0; iter < numToGrow; iter++) {
        std::cout << "Beginning iteration " << iter + 1 << " of " << _numStates + numToGrow <<std::endl;
        scores.clear();
        
        //split each state
        for (int imodel = 0; imodel < numStates; imodel++) {
            hmms.push_back(HmmSharedPtr_t(best->splitState(imodel,true,true)));
        }
        
        //train each state
        for (int imodel = 0; imodel < numStates; imodel++) {
            std::cout << "Training model " << imodel + 1 << " of " << numStates << std::endl;
            scores.push_back(train(hmms[imodel],meas,true,false));
        }
        
        //get best one
        
        std::cout << "SCORES: " << scores << std::endl;
        const int bestIdx = getArgMaxInVec(scores);
        const HmmFloat_t bestScore = scores[bestIdx];
        
        if (lastScore < bestScore) {
            
            best = hmms[bestIdx];
            
            std::cout << "picked model " << bestIdx + 1 << std::endl;
            std::cout << "BEST SCORE: " <<  scores[bestIdx] << std::endl;

        }
        else {
            std::cout << "TERMINATING BECAUSE MODEL DID NOT IMPROVE" << std::endl;
            worked = false;
        }
        
        lastScore = bestScore;
        
        
        
       
        
        numStates++;
        
        hmms.clear();
        
        if (!worked) {
            break;
        }
        
    }
    
    *this = *best.get();
    
    
}



StateSegmentVec_t HiddenMarkovModel::getStateInfo(const ViterbiPath_t & path, const uint32_t nstate) const {
    
    
    StateSegmentVec_t segs;
        
    segs.reserve(path.size() / 2);
    
    bool inSegment = false;
    uint32_t startIndex;
    uint32_t fromIndex = 0;
    
    for (int t = 0; t < path.size(); t++) {
        if (path[t] == nstate) {
            
            if (inSegment) {
                continue;
            }
            
            inSegment = true;
            startIndex = t;
            if (t != 0) {
                fromIndex = path[t-1];
            }
        }
        else {
            if (!inSegment) {
                continue;
            }
            
            StateSegment_t seg;
            
            seg.timeIndices = std::make_pair(startIndex,t-1);
            seg.fromAndToStates = std::make_pair(fromIndex, path[t]);
            
            segs.push_back(seg);
            
            inSegment = false;
        }
    }

    return segs;
}


void HiddenMarkovModel::printStateTransitionMatrix() const {
    for (int i = 0; i < _A.size(); i++) {
        std::cout << _A[i] << std::endl;
    }

}


