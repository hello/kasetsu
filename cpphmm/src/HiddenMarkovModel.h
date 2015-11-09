#ifndef _HIDDENMARKOVMODEL_H_
#define _HIDDENMARKOVMODEL_H_

#include "HmmHelpers.h"
#include "ReestimationResult.h"
#include "SaveStateInterface.h"
#include <cmath>
/*  
      does forwards backwards calcs, computes gamma, xi, etc.
 
      this class is stateful.
 */






typedef std::pair<uint32_t,uint32_t> Segment_t;

typedef struct {
    Segment_t timeIndices;
    Segment_t fromAndToStates;
} StateSegment_t;

typedef std::vector<StateSegment_t> StateSegmentVec_t;


class HiddenMarkovModel;

typedef SHARED_PTR<HiddenMarkovModel> HmmSharedPtr_t;


class HiddenMarkovModel {
public:
    HiddenMarkovModel(const HiddenMarkovModel & copyme);
    HiddenMarkovModel(const HmmDataMatrix_t & A,SaveStateInterface * stateSaver = NULL);
    
    ~HiddenMarkovModel();
    HiddenMarkovModel & operator = (const HiddenMarkovModel & hmm);

    
    void addModelForState(HmmPdfInterfaceSharedPtr_t);
    
    ReestimationResult_t reestimate(const HmmDataMatrix_t & meas,bool dontReestimateIfScoreDidNotImprove = false, const HmmFloat_t minValueForA = 0.0);
    ReestimationResult_t reestimateViterbi(const HmmDataMatrix_t & meas);
    HmmFloat_t getModelCost(const HmmDataMatrix_t & meas) const;
    ViterbiDecodeResult_t decode(const HmmDataMatrix_t & meas) const;
    bool reestimateViterbiSplitState(uint32_t s1, uint32_t s2,const ViterbiPath_t & originalViterbi,const HmmDataMatrix_t & meas, bool reestimateMeas);
    
    void enlargeWithVSTACS(const HmmDataMatrix_t & meas,uint32_t numToGrow) ;
    StateSegmentVec_t getStateInfo(const ViterbiPath_t & path, const uint32_t nstate) const;
    void printStateTransitionMatrix() const;


    std::string serializeToJson() const;
    HmmSharedPtr_t splitState(uint32_t stateToSplit,bool perturbSelfTerm,bool perturbMeasurements) const;
    HmmSharedPtr_t deleteStates(UIntSet_t statesToDelete) const;

    uint32_t getNumberOfFreeParams() const;




private:
    
    
    AlphaBetaResult_t getAlphaAndBeta(int32_t numObs,const HmmDataVec_t & pi, const HmmDataMatrix_t & logbmap, const HmmDataMatrix_t & A) const;
    HmmDataMatrix_t getLogBMap(const ModelVec_t & models,const HmmDataMatrix_t & meas) const;
    
    Hmm3DMatrix_t getLogXi(const AlphaBetaResult_t & alphabeta,const HmmDataMatrix_t & logbmap,size_t numObs) const;
    HmmDataMatrix_t getLogGamma(const AlphaBetaResult_t & alphabeta,size_t numObs) const;
    HmmDataMatrix_t reestimateA(const Hmm3DMatrix_t & xi, const HmmDataMatrix_t & gamma,const size_t numObs,const HmmFloat_t damping,const HmmFloat_t minValueForA) const;
    ModelVec_t reestimateFromGamma(const HmmDataMatrix_t & gamma, const HmmDataMatrix_t & meas, const HmmFloat_t eta) const;
    
    HmmDataMatrix_t getGammaFromViterbiPath(const ViterbiPath_t & path,const size_t numStates, const size_t numObs) const;
    HmmDataMatrix_t reestimateAFromViterbiPath(const ViterbiPath_t & path, const HmmDataMatrix_t & meas,size_t numObs,size_t numStates,const HmmDataMatrix_t & originalA) const;

    ViterbiDecodeResult_t decodePathAndGetCost(int32_t startidx,const ViterbiPathMatrix_t & paths,const HmmDataMatrix_t & phi) const;

    ModelVec_t _models;
    uint32_t _numStates;
    HmmDataMatrix_t _A;
    HmmDataVec_t _pi;
    
    SaveStateInterface * _stateSaver;

    
};

#endif //_HIDDENMARKOVMODEL_H_
