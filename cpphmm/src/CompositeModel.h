#ifndef _COMPOSITEMODEL_H_
#define _COMPOSITEMODEL_H_

#include "HmmPdfInterface.h"

class CompositeModel : public HmmPdfInterface {
public:
    CompositeModel();
    ~CompositeModel();
    
    HmmDataVec_t getLogOfPdf(const HmmDataMatrix_t & x);
    
    
};

#endif //_COMPOSITEMODEL_H_
