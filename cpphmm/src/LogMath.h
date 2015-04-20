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
    if (logx == LOGZERO && logy == LOGZERO) {
        return LOGZERO;
    }
    else if (logx == LOGZERO) {
        return logy;
    }
    else if (logy == LOGZERO) {
        return logx;
    }
    else {
        if (logx > logy) {
            return logx + eln(1.0 + eexp(logy - logx));
        }
        else {
            return logy + eln(1.0 + eexp(logx - logy));
        }
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
