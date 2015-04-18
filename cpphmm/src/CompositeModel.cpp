
#include "CompositeModel.h"

#include <iostream>
#include <sstream>

#include "SerializationHelpers.h"

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
    CompositeModel * newModel = new CompositeModel();
    
    for (ModelVec_t::const_iterator vecIterator = _models.begin();
         vecIterator != _models.end(); vecIterator++) {
        
        const HmmPdfInterface * const model = *vecIterator;
    
        newModel->addModel(model->reestimate(gammaForThisState, meas));
    
    }
    
    return newModel;
}

HmmDataVec_t CompositeModel::getLogOfPdf(const HmmDataMatrix_t & x) const {
    HmmDataVec_t vec;
    vec.resize(x[0].size());
    
    //log of 1 is 0
    memset(vec.data(),0,sizeof(HmmFloat_t)*vec.size());

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

std::string CompositeModel::serializeToJson() const {
    return vecToJsonArray<ModelVec_t,PdfInterfaceSerializationAdapter<ModelVec_t::value_type>>(_models);
}
