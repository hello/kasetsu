
#ifndef _TRAINER_H_
#define _TRAINER_H_

#include "HiddenMarkovModel.h"

class Trainer {
public:
    static bool train (HiddenMarkovModel * hmm,const HmmDataMatrix_t & meas);
};

#endif //_TRAINER_H_
