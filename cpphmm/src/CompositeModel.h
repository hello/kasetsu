#ifndef _COMPOSITEMODEL_H_
#define _COMPOSITEMODEL_H_

#include "HmmPdfInterface.h"

class CompositeModel : public HmmPdfInterface {
public:
    CompositeModel();
    ~CompositeModel();
    
    void addModel(HmmPdfInterface * model);
    HmmPdfInterface * clone(bool isPerturbed) const;
    HmmPdfInterface * reestimate(const HmmDataVec_t & gammaForThisState, const HmmDataMatrix_t & meas) const;

    HmmDataVec_t getLogOfPdf(const HmmDataMatrix_t & x) const;
    
    std::string serializeToJson() const;
private:
        
    ModelVec_t _models;
    
    
};

#endif //_COMPOSITEMODEL_H_
