#ifndef _MULTIOBSSEQUENCEHIDDENMARKOVMODEL_H_
#define _MULTIOBSSEQUENCEHIDDENMARKOVMODEL_H_

#include "HmmPdfInterface.h"
#include "MultiObsSequence.h"

class MultiObsHiddenMarkovModel {
public:
    MultiObsHiddenMarkovModel(const ModelVec_t &models,const HmmDataMatrix_t & A);
    ~MultiObsHiddenMarkovModel();
    
    void reestimate(const MultiObsSequence & meas);
private:
    
    ModelVec_t _models;
    uint32_t _numStates;
    HmmDataMatrix_t _A;
    HmmDataVec_t _pi;
    
};

#endif //_MULTIOBSSEQUENCEHIDDENMARKOVMODEL_H_
