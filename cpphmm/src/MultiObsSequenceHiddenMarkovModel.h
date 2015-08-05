#ifndef _MULTIOBSSEQUENCEHIDDENMARKOVMODEL_H_
#define _MULTIOBSSEQUENCEHIDDENMARKOVMODEL_H_

#include "HmmPdfInterface.h"
#include "MultiObsSequence.h"

class MultiObsHiddenMarkovModel {
public:
    MultiObsHiddenMarkovModel(const HmmDataMatrix_t &initalAlphabetProbs,const HmmDataMatrix_t & A);
    ~MultiObsHiddenMarkovModel();
    
    void reestimate(const MultiObsSequence & meas);
    
    HmmDataMatrix_t getAMatrix() const;
    HmmDataMatrix_t getAlphabetMatrix() const;
    HmmDataMatrix_t getLogBMap(const HmmDataMatrix_t & rawdata,const HmmDataMatrix_t & alphabetProbs) const;

private:

    HmmDataMatrix_t _ANumerator;
    HmmDataMatrix_t _alphabetNumerator;
    HmmDataVec_t _logDenominator;
    HmmDataVec_t _pi;

    uint32_t _numStates;

    
};

#endif //_MULTIOBSSEQUENCEHIDDENMARKOVMODEL_H_
