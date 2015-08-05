#ifndef _MULTIOBSSEQUENCEHIDDENMARKOVMODEL_H_
#define _MULTIOBSSEQUENCEHIDDENMARKOVMODEL_H_

#include "HmmPdfInterface.h"
#include "MultiObsSequence.h"

class MultiObsHiddenMarkovModel {
public:
    MultiObsHiddenMarkovModel(const HmmDataMatrix_t &initalAlphabetProbs,const HmmDataMatrix_t & A);
    ~MultiObsHiddenMarkovModel();
    
    void reestimate(const MultiObsSequence & meas);
private:
    
    HmmDataMatrix_t _ANumerator;
    HmmDataMatrix_t _alphabetNumerator;
    HmmDataVec_t _gammaCount;
    HmmDataVec_t _pi;

    uint32_t _numStates;

    
};

#endif //_MULTIOBSSEQUENCEHIDDENMARKOVMODEL_H_
