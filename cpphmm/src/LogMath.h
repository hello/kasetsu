#ifndef _LOGMATH_H_
#define _LOGMATH_H_

#include <cmath>
#include <limits>
#include "HmmTypes.h"


#define MIN_NUMBER (std::numeric_limits<HmmFloat_t>::min() * 2)
#define LOGZERO  (-INFINITY)

inline HmmFloat_t eexp(const HmmFloat_t x) {
    if (x == LOGZERO) {
        return 0.0;
    }
    else {
        return exp(x);
    }
}

inline HmmFloat_t eln(const HmmFloat_t x) {
    //if x is zero
    if (x <= MIN_NUMBER) {
        return LOGZERO;
    }
    else {
        return log(x);
    }
}

inline HmmFloat_t elnsum(const HmmFloat_t logx, const HmmFloat_t logy) {
    const HmmFloat_t x = eexp(logx);
    const HmmFloat_t y = eexp(logy);
    
    //if x and y are zero
    if (x > MIN_NUMBER && y > MIN_NUMBER ) {
        return eln(x + y);
    }
    // if x is zero
    else if (x > MIN_NUMBER) {
        return logx;
    }
    else if (y > MIN_NUMBER) {
        return logy;
    }
    else {
        return LOGZERO;
    }
}

inline HmmFloat_t elnproduct(const HmmFloat_t logx, const HmmFloat_t logy) {
    if (logx == LOGZERO || logy == LOGZERO) {
        return LOGZERO;
    }
    else {
        return logx + logy;
    }
}

#endif //_LOGMATH_H_
