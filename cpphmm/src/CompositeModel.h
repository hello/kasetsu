#ifndef _COMPOSITEMODEL_H_
#define _COMPOSITEMODEL_H_

#include "HmmPdfInterface.h"

class CompositeModel : public HmmPdfInterface {
public:
    CompositeModel();
    ~CompositeModel();
    
    HmmPdfInterface * reestimate(const HmmDataMatrix_t & gamma, const HmmDataMatrix_t & meas) const;

    HmmDataVec_t getLogOfPdf(const HmmDataMatrix_t & x) const;
    
    
};

#endif //_COMPOSITEMODEL_H_
