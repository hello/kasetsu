#ifndef _SIGNALGENERATOR_H_
#define _SIGNALGENERATOR_H_

#include "HmmTypes.h"

HmmDataVec_t getGammaSignal(const int length,const HmmDataMatrix_t & A, const HmmDataVec_t & means, const HmmDataVec_t & stddevs );
HmmDataVec_t getPoissonSignal(const int length, const HmmDataMatrix_t & A, const HmmDataVec_t & means);

HmmDataVec_t getAlphabetSignal(const int length, const HmmDataMatrix_t & A, const HmmDataMatrix_t & alphabet);

#endif //_SIGNALGENERATOR_H_
