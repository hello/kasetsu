#ifndef _MULTIOBSSEQUENCEHIDDENMARKOVMODEL_H_
#define _MULTIOBSSEQUENCEHIDDENMARKOVMODEL_H_

#include "HmmPdfInterface.h"
#include "MultiObsSequence.h"
#include "HmmHelpers.h"

class MultiObsHiddenMarkovModel {
public:
    MultiObsHiddenMarkovModel(const MatrixMap_t & initialAlphabetProbs,const HmmDataMatrix_t & A);
    ~MultiObsHiddenMarkovModel();
    
    void reestimate(const MultiObsSequence & meas,const uint32_t numIter);
    
    HmmDataMatrix_t getAMatrix() const;
    MatrixMap_t getAlphabetMatrix() const;
    HmmDataMatrix_t getLogBMap(const MatrixMap_t & rawdataMap, const MatrixMap_t & alphabetProbsMap) const;

private:

    HmmDataMatrix_t _ANumerator;
    MatrixMap_t _alphabetNumerator;
    HmmDataVec_t _logDenominator;
    HmmDataVec_t _pi;
    
    uint32_t _numStates;

    
};

#endif //_MULTIOBSSEQUENCEHIDDENMARKOVMODEL_H_
