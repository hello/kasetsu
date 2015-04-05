
#include "CompositeModel.h"


CompositeModel::CompositeModel() {
    
}

CompositeModel::~CompositeModel() {
    
}

HmmPdfInterface * CompositeModel::reestimate(const HmmDataMatrix_t & gamma, const HmmDataMatrix_t & meas) const {
    return NULL;
}

HmmDataVec_t CompositeModel::getLogOfPdf(const HmmDataMatrix_t & x) const {
    return HmmDataVec_t();
}

