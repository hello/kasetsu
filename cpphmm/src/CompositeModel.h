#ifndef _COMPOSITEMODEL_H_
#define _COMPOSITEMODEL_H_

#include "HmmPdfInterface.h"

class CompositeModel : public HmmPdfInterface {
public:
    CompositeModel();
    ~CompositeModel();
    
    void addModel(HmmPdfInterfaceSharedPtr_t model);
    HmmPdfInterfaceSharedPtr_t clone(bool isPerturbed) const;
    HmmPdfInterfaceSharedPtr_t reestimate(const HmmDataVec_t & gammaForThisState, const HmmDataMatrix_t & meas, const HmmFloat_t eta) const;

    HmmDataVec_t getLogOfPdf(const HmmDataMatrix_t & x) const;
    
    std::string serializeToJson() const;
    uint32_t getNumberOfFreeParams() const;
private:
        
    ModelVec_t _models;
    
    
};

#endif //_COMPOSITEMODEL_H_
