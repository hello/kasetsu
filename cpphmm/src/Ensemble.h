#ifndef _ENSEMBLE_H_
#define _ENSEMBLE_H_

#include "MultiObsSequenceHiddenMarkovModel.h"


class Ensemble {
public:
    Ensemble(const MultiObsHiddenMarkovModel & seed);
    Ensemble(const HmmVec_t & hmms);

    ~Ensemble();
    
    TransitionAtTimeVec_t evaluatePaths(const MultiObsSequence & meas, const int32_t toleranceForError, bool verbose) const;
    
    void grow(const MultiObsSequence & meas, uint32_t n);
    
    void evaluate(const MultiObsSequence & meas,bool verbose);
    
    HmmVec_t getModelPointers() const ;
    
private:
    
    HmmVec_t _models;
};

#endif
