#ifndef _MULTIOBSSEQUENCEHIDDENMARKOVMODEL_H_
#define _MULTIOBSSEQUENCEHIDDENMARKOVMODEL_H_

#include "HmmPdfInterface.h"
#include "MultiObsSequence.h"
#include "HmmHelpers.h"
#include <vector>

class MultiObsHiddenMarkovModel {
public:
    MultiObsHiddenMarkovModel(const MatrixMap_t & initialAlphabetProbs,const HmmDataMatrix_t & A,const TransitionVector_t & forbiddenMotionTransitions);
    MultiObsHiddenMarkovModel(const MatrixMap_t & logAlphabetNumerator,const HmmDataMatrix_t & logANumerator, const HmmDataVec_t & logDenominator,const TransitionVector_t & forbiddenMotiontransitions,const HmmFloat_t scalingFactor = 1.0);

    ~MultiObsHiddenMarkovModel();
    
    std::vector<ViterbiDecodeResult_t> evaluatePaths(const MultiObsSequence & meas, const int32_t toleranceForError) ;
    void reestimate(const MultiObsSequence & meas,const uint32_t numIter,const uint32_t priorWeightAsNumberOfSamples);
    HmmDataMatrix_t getAMatrix() const;
    MatrixMap_t getAlphabetMatrix() const;
    HmmDataMatrix_t getLogBMap(const MatrixMap_t & rawdataMap, const MatrixMap_t & alphabetProbsMap) const;
    HmmDataMatrix_t getLastConfusionMatrix() const;
    
    const HmmDataVec_t & getPi() const;
    const HmmDataMatrix_t & getLogANumerator() const;
    const MatrixMap_t & getLogAlphabetNumerator() const;
    const HmmDataVec_t & getLogDenominator() const;
    uint32_t getNumStates() const;
    UIntVec_t getMinStatedDurations() const;
    const TransitionVector_t & getForbiddenMotionTransitions() const;

private:

    void scale(const HmmFloat_t scaleFactor);
    
    HmmDataMatrix_t _A;

    HmmDataMatrix_t _logANumerator;
    MatrixMap_t _logAlphabetNumerator;
    HmmDataVec_t _logDenominator;
    HmmDataVec_t _pi;
    HmmDataMatrix_t _lastConfusionMatrix;
    
    uint32_t _numStates;

    TransitionVector_t _forbiddenMotionTransitions; //misnomer, should be called forbidden transitions where there is no motion at all
    
};

#endif //_MULTIOBSSEQUENCEHIDDENMARKOVMODEL_H_
