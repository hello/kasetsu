#include "RandomHelpers.h"
#include <random>

//between -1 and 1
HmmFloat_t getRandomFloat() {
    const float r = 2.0 * static_cast <HmmFloat_t> (rand()) / static_cast <HmmFloat_t> (RAND_MAX) - 1.0;
    return r;
}

UIntVec_t getBoundedRandomSeq(uint32_t lowerLimit, uint32_t upperLimit, uint32_t len) {
    UIntVec_t ret;
    const uint32_t range = upperLimit - lowerLimit;

    for (int i = 0; i < len; i++) {
        ret.push_back(lowerLimit + (rand() % range));
    }
    
    
    return ret;
}
