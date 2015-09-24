#ifndef _MULTIOBSSEQUENCEHIDDENMARKOVMODEL_H_
#define _MULTIOBSSEQUENCEHIDDENMARKOVMODEL_H_

#include "HmmPdfInterface.h"
#include "MultiObsSequence.h"
#include "HmmHelpers.h"
#include "TransitionRestrictionInterface.h"

#include <vector>

class MultiObsHiddenMarkovModel;

typedef std::vector<ViterbiDecodeResult_t> ViterbiResultVec_t;
typedef SHARED_PTR<MultiObsHiddenMarkovModel> MultiObsHmmSharedPtr_t;
typedef std::vector<MultiObsHmmSharedPtr_t> HmmVec_t;


typedef struct {
    ViterbiResultVec_t paths;
    HmmDataMatrix_t confusionMatrix;
    HmmDataMatrix_t confusionCount;
} EvaluationResult_t;

class MultiObsHiddenMarkovModel {
public:
    MultiObsHiddenMarkovModel(const MatrixMap_t & initialAlphabetProbs,const HmmDataMatrix_t & A,TransitionRestrictionVector_t forbiddenTransitions);
    MultiObsHiddenMarkovModel(const MatrixMap_t & logAlphabetNumerator,const HmmDataMatrix_t & logANumerator, const HmmDataVec_t & logDenominator,const TransitionRestrictionVector_t forbiddenTransitions,const HmmFloat_t scalingFactor = 1.0);

    ~MultiObsHiddenMarkovModel();
    
    EvaluationResult_t evaluatePaths(const MultiObsSequence & meas, const int32_t toleranceForError = 4, bool verbose = false) const;
    void reestimate(const MultiObsSequence & meas,const uint32_t numIter,const HmmFloat_t priorWeightAsNumberOfSamples);
    HmmDataMatrix_t getAMatrix() const;
    MatrixMap_t getAlphabetMatrix() const;
    HmmDataMatrix_t getLogBMap(const MatrixMap_t & rawdataMap, const MatrixMap_t & alphabetProbsMap) const;
    
    const HmmDataVec_t & getPi() const;
    const HmmDataMatrix_t & getLogANumerator() const;
    const MatrixMap_t & getLogAlphabetNumerator() const;
    const HmmDataVec_t & getLogDenominator() const;
    uint32_t getNumStates() const;
    UIntVec_t getMinStatedDurations() const;
    
    const TransitionRestrictionVector_t & getTransitionRestrictions() const ;

private:

    void scale(const HmmFloat_t scaleFactor);
    
    HmmDataMatrix_t _A;

    HmmDataMatrix_t _logANumerator;
    MatrixMap_t _logAlphabetNumerator;
    HmmDataVec_t _logDenominator;
    HmmDataVec_t _pi;
    
    uint32_t _numStates;
    
    TransitionRestrictionVector_t _forbiddenTransitions;
    
    TransitionMultiMap_t getForbiddenTransitions(const MatrixMap_t & measurements) const;
      

    
};

#endif //_MULTIOBSSEQUENCEHIDDENMARKOVMODEL_H_
