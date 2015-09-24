#ifndef _RANDOMHELPERS_H_
#define _RANDOMHELPERS_H_

#include "HmmTypes.h"


HmmFloat_t getRandomFloat();

UIntVec_t getBoundedRandomSeq(uint32_t lowerLimit, uint32_t upperLimit, uint32_t len);


#endif //_RANDOMHELPERS_H_

