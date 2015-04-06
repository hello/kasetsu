
#include "CompositeModel.h"


CompositeModel::CompositeModel() {
    
}

void CompositeModel::addModel(HmmPdfInterface * model) {
    _models.push_back(model);
}


CompositeModel::~CompositeModel() {

    for (ModelVec_t::iterator vecIterator = _models.begin();
        vecIterator != _models.end(); vecIterator++) {
            
        delete *vecIterator;
        *vecIterator = NULL;
    }
    
}

HmmPdfInterface * CompositeModel::reestimate(const HmmDataVec_t & gammaForThisState, const HmmDataMatrix_t & meas) const {
    return NULL;
}

HmmDataVec_t CompositeModel::getLogOfPdf(const HmmDataMatrix_t & x) const {
    HmmDataVec_t vec;
    vec.resize(x.size());
    
    //log of 0 is 1
    for (int32_t i = 0; i < vec.size(); i++) {
        vec[i] = 1.0f;
    }
    
    
    for (ModelVec_t::const_iterator vecIterator = _models.begin();
             vecIterator != _models.end(); vecIterator++) {

        const HmmPdfInterface * const model = *vecIterator;
            
        const HmmDataVec_t eval = model->getLogOfPdf(x);
            
        for (int32_t i = 0; i < vec.size(); i++) {
            vec[i] += eval[i];
        }

        
    }
    
    return vec;
}

