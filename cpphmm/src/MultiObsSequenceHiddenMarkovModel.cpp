#include "MultiObsSequenceHiddenMarkovModel.h"
#include "CompositeModel.h"
#include "HmmHelpers.h"

#include "ThreadPool.h"



MultiObsHiddenMarkovModel::MultiObsHiddenMarkovModel(const ModelVec_t &models,const HmmDataMatrix_t & A) {
    
    _A = A;
    _models = models;
    _numStates = _models.size();
}

MultiObsHiddenMarkovModel::~MultiObsHiddenMarkovModel() {
    
}



void MultiObsHiddenMarkovModel::reestimate(const MultiObsSequence & meas) {
    
    
    
    
    for (int iSequence = 0; iSequence < meas.size(); iSequence++) {
        const HmmDataMatrix_t & rawdata = meas.getMeasurements(iSequence);
        const LabelMap_t & labels = meas.getLabels(iSequence);
        const TransitionMultiMap_t & forbiddenTransitions = meas.getForbiddenTransitions(iSequence);
        
        HmmHelpers::getAlphaAndBeta(<#int32_t numObs#>, <#const HmmDataVec_t &pi#>, <#const HmmDataMatrix_t &logbmap#>, _A, _numStates,labels,forbiddenTransitions)

    }
    
    
    
    
}

