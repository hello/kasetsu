#include "MultiObsSequenceHiddenMarkovModel.h"
#include "CompositeModel.h"
#include "HmmHelpers.h"
#include "MatrixHelpers.h"
#include "ThreadPool.h"
#include "LogMath.h"


MultiObsHiddenMarkovModel::MultiObsHiddenMarkovModel(const HmmDataMatrix_t & initialAlphabetProbs,const HmmDataMatrix_t & A) {
    
    _numStates = initialAlphabetProbs.size();
    _logDenominator.reserve(_numStates);
    
    for (int i = 0; i < _numStates; i++) {
        _logDenominator.push_back(0.0);
    }
    
    _alphabetNumerator = getELNofMatrix(initialAlphabetProbs);
    _ANumerator = getELNofMatrix(A);
    _pi = getUniformVec(_numStates);
}

MultiObsHiddenMarkovModel::~MultiObsHiddenMarkovModel() {
    
}


HmmDataMatrix_t MultiObsHiddenMarkovModel::getAMatrix() const {
    //construct transition matrix
    HmmDataMatrix_t A = _ANumerator;
    for (int iState = 0; iState < _numStates; iState++) {
        for (int j = 0; j < _numStates; j++) {
            A[iState][j] = eexp(elnproduct(_ANumerator[iState][j], -_logDenominator[iState]));
        }
    }
    
    return A;
}

HmmDataMatrix_t MultiObsHiddenMarkovModel::getAlphabetMatrix() const {
    const uint32_t alphabetSize = _alphabetNumerator[0].size();

    //construct alphabet probs
    HmmDataMatrix_t alphabetProbs = _alphabetNumerator;
    for (int iState = 0; iState < _numStates; iState++) {
        for (int iAlphabet = 0; iAlphabet < alphabetSize; iAlphabet++) {
            alphabetProbs[iState][iAlphabet] = eexp(elnproduct(_alphabetNumerator[iState][iAlphabet], -_logDenominator[iState]));
        }
    }
    
    return alphabetProbs;
}

HmmDataMatrix_t MultiObsHiddenMarkovModel::getLogBMap(const HmmDataMatrix_t & rawdata, const HmmDataMatrix_t & alphabetProbs) const {
    HmmDataMatrix_t logbmap;
    const uint32_t numObs = rawdata[0].size();
    
    //get logbmap
    for (int iState = 0; iState < _numStates; iState++) {
        HmmDataVec_t logeval;
        logeval.reserve(numObs);
        
        for (int t = 0; t < numObs; t++) {
            const uint32_t idx = (uint32_t)rawdata[0][t];
            logeval.push_back(eln(alphabetProbs[iState][idx]));
        }
        
        logbmap.push_back(logeval);
    }
    
    return logbmap;
}



void MultiObsHiddenMarkovModel::reestimate(const MultiObsSequence & meas,const uint32_t numIter) {
    
    const uint32_t alphabetSize = _alphabetNumerator[0].size();
    
    for (int iter = 0; iter < numIter; iter++) {
        for (int iSequence = 0; iSequence < meas.size(); iSequence++) {
            const HmmDataMatrix_t & rawdata = meas.getMeasurements(iSequence);
            const LabelMap_t & labels = meas.getLabels(iSequence);
            const TransitionMultiMap_t & forbiddenTransitions = meas.getForbiddenTransitions(iSequence);
            
            if (rawdata.empty()) {
                continue;
            }
            
            const uint32_t numObs = rawdata[0].size();
            
            
            HmmDataMatrix_t alphabetProbs = getAlphabetMatrix();
            
            HmmDataMatrix_t A = getAMatrix();
            
            HmmDataMatrix_t logbmap = getLogBMap(rawdata,alphabetProbs);
            
            const AlphaBetaResult_t alphaBeta = HmmHelpers::getAlphaAndBeta(numObs, _pi, logbmap, A, _numStates,labels,forbiddenTransitions);
            
            const HmmDataMatrix_t logANumerator = HmmHelpers::getLogANumerator(alphaBeta, logbmap, forbiddenTransitions, numObs, _numStates);
            
            const HmmDataMatrix_t logAlphabetNumerator = HmmHelpers::getLogAlphabetNumerator(alphaBeta, rawdata[0], _numStates, numObs, alphabetSize);
            
            const HmmDataVec_t logDenominator = HmmHelpers::getLogDenominator(alphaBeta, _numStates, numObs);
            
            
            if (iSequence == 0) {
                _ANumerator = logANumerator;
                _alphabetNumerator = logAlphabetNumerator;
                _logDenominator = logDenominator;
            }
            else {
                _ANumerator = HmmHelpers::elnAddMatrix(_ANumerator, logANumerator);
                _alphabetNumerator = HmmHelpers::elnAddMatrix(_alphabetNumerator, logAlphabetNumerator);
                _logDenominator = HmmHelpers::elnAddVector(_logDenominator, logDenominator);
            }
            
            
            
            
            printMat("A2", getAMatrix());
            printMat("alphabet2", getAlphabetMatrix());
            printVec("gammacount", _logDenominator);
            
        }
    }
}

