#include "ReestimationResult.h"


ReestimationResult_t::ReestimationResult_t()
:_isValid(false)
,_totalloglik(0.0)
{}

ReestimationResult_t::ReestimationResult_t(const HmmFloat_t totalloglik)
:_isValid(true)
,_totalloglik(totalloglik)
{}

bool ReestimationResult_t::isValid() const {
    return _isValid;
}

HmmFloat_t ReestimationResult_t::getLogLikelihood() const {
    return _totalloglik;
}

