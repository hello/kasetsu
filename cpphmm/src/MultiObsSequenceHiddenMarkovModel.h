#ifndef _MULTIOBSSEQUENCEHIDDENMARKOVMODEL_H_
#define _MULTIOBSSEQUENCEHIDDENMARKOVMODEL_H_

#include "HmmPdfInterface.h"
#include "MultiObsSequence.h"
#include "HmmHelpers.h"
#include <vector>

class MultiObsHiddenMarkovModel {
public:
    MultiObsHiddenMarkovModel(const MatrixMap_t & initialAlphabetProbs,const HmmDataMatrix_t & A);
    ~MultiObsHiddenMarkovModel();
    
    std::vector<ViterbiDecodeResult_t> evaluatePaths(const MultiObsSequence & meas) const ;
    void reestimate(const MultiObsSequence & meas,const uint32_t numIter);
    HmmDataVec_t getPi() const;
    HmmDataMatrix_t getAMatrix() const;
    MatrixMap_t getAlphabetMatrix() const;
    HmmDataMatrix_t getLogBMap(const MatrixMap_t & rawdataMap, const MatrixMap_t & alphabetProbsMap) const;
    HmmDataMatrix_t getLastConfusionMatrix() const;
private:

    HmmDataMatrix_t _ANumerator;
    MatrixMap_t _alphabetNumerator;
    HmmDataVec_t _logDenominator;
    HmmDataVec_t _pi;
    HmmDataMatrix_t _lastConfusionMatrix;
    
    uint32_t _numStates;

    
};

#endif //_MULTIOBSSEQUENCEHIDDENMARKOVMODEL_H_
