#include "RandomHelpers.h"
#include <random>

//between -1 and 1
HmmFloat_t getRandomFloat() {
    const float r = 2.0 * static_cast <HmmFloat_t> (rand()) / static_cast <HmmFloat_t> (RAND_MAX) - 1.0;
    return r;
}
