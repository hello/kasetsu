#include "MultiObsSequenceHiddenMarkovModel.h"
#include "CompositeModel.h"
#include "HmmHelpers.h"
#include "MatrixHelpers.h"
#include "ThreadPool.h"



MultiObsHiddenMarkovModel::MultiObsHiddenMarkovModel(const ModelVec_t &models,const HmmDataMatrix_t & A) {
    
    _A = A;
    _models = models;
    _numStates = _models.size();
    
    _pi = getUniformVec(_numStates);
}

MultiObsHiddenMarkovModel::~MultiObsHiddenMarkovModel() {
    
}



void MultiObsHiddenMarkovModel::reestimate(const MultiObsSequence & meas) {
    
    
    const HmmFloat_t damping = 0.1;
    const HmmFloat_t min_value_for_a = 1e-6;
    
    for (int iSequence = 0; iSequence < meas.size(); iSequence++) {
        const HmmDataMatrix_t & rawdata = meas.getMeasurements(iSequence);
        const LabelMap_t & labels = meas.getLabels(iSequence);
        const TransitionMultiMap_t & forbiddenTransitions = meas.getForbiddenTransitions(iSequence);
        
        
        if (rawdata.empty()) {
            continue;
        }
        
        const uint32_t numObs = rawdata[0].size();

        HmmDataMatrix_t logbmap;

        //get logbmap
        for (ModelVec_t::const_iterator it = _models.begin(); it != _models.end(); it++) {
            logbmap.push_back((*it)->getLogOfPdf(rawdata));
        }
        
        //get forward and backward calc
        const AlphaBetaResult_t alphaBeta = HmmHelpers::getAlphaAndBeta(numObs, _pi, logbmap, _A, _numStates,labels,forbiddenTransitions);
        
        
        const Hmm3DMatrix_t logxi = HmmHelpers::getLogXi(alphaBeta, logbmap,forbiddenTransitions,numObs, _numStates);
        
        
        const HmmDataMatrix_t logGamma = HmmHelpers::getLogGamma(alphaBeta, numObs, _numStates);
        
        const HmmDataMatrix_t A2 = HmmHelpers::reestimateA(_A, logxi, logGamma, numObs, damping, min_value_for_a, _numStates);
        
        
        const HmmDataMatrix_t gamma = getEEXPofMatrix(logGamma);
        
        ModelVec_t updatedModels;
        
        for (size_t iState = 0; iState < _numStates; iState++) {
            
            const HmmDataVec_t & gammaForThisState = gamma[iState];
            
            HmmPdfInterfaceSharedPtr_t newModel = _models[iState]->reestimate(gammaForThisState, rawdata,damping);
            
            updatedModels.push_back(newModel);
        }

        

    }
    
    
    
    
}

