#ifndef _ENSEMBLE_H_
#define _ENSEMBLE_H_

#include "MultiObsSequenceHiddenMarkovModel.h"


class Ensemble {
public:
    Ensemble(const MultiObsHiddenMarkovModel & seed);
    ~Ensemble();
    
    TransitionAtTimeVec_t evaluatePaths(const MultiObsSequence & meas, const int32_t toleranceForError, bool verbose) const;
    
    void grow(const MultiObsSequence & meas, uint32_t n);
    
    HmmVec_t getModelPointers() const ;
    
private:
    
    HmmVec_t _models;
};

#endif
