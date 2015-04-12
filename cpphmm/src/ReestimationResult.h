#ifndef _REESTIMATIONRESULT_H_
#define _REESTIMATIONRESULT_H_

#include "HmmTypes.h"

class ReestimationResult_t {
public:
    
    ReestimationResult_t();
    ReestimationResult_t(const HmmFloat_t totalloglik);
    
    bool isValid() const;
    HmmFloat_t getLogLikelihood() const;
        
private:
    
    bool _isValid;
    HmmFloat_t _totalloglik;
};

#endif //_REESTIMATIONRESULT_H_
