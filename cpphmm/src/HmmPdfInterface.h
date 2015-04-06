#ifndef HMMPDFINTERFACE_H_
#define HMMPDFINTERFACE_H_

#include "HmmTypes.h"

class HmmPdfInterface {
public:
    virtual ~HmmPdfInterface() {};
    virtual HmmDataVec_t getLogOfPdf(const HmmDataMatrix_t & x) const = 0;
    virtual HmmPdfInterface * reestimate(const HmmDataVec_t & gammaForThisState, const HmmDataMatrix_t & meas) const = 0;
};

#endif //HMMPDFINTERFACE_H_
