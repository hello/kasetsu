#include "MultiObsSequenceHiddenMarkovModel.h"
#include "CompositeModel.h"
#include "HmmHelpers.h"
#include "MatrixHelpers.h"
#include "ThreadPool.h"
#include "LogMath.h"


MultiObsHiddenMarkovModel::MultiObsHiddenMarkovModel(const HmmDataMatrix_t & initialAlphabetProbs,const HmmDataMatrix_t & A) {
    
    _ANumerator = A;
    _numStates = initialAlphabetProbs.size();
    _gammaCount.reserve(_numStates);
    
    for (int i = 0; i < _numStates; i++) {
        _gammaCount.push_back(1.0);
    }
    
    _alphabetNumerator = initialAlphabetProbs;
    _pi = getUniformVec(_numStates);
}

MultiObsHiddenMarkovModel::~MultiObsHiddenMarkovModel() {
    
}



void MultiObsHiddenMarkovModel::reestimate(const MultiObsSequence & meas) {
    
    int iState,iAlphabet;
    int i,j,t;
    
    const HmmFloat_t min_value_for_a = 1e-6;
    
    const uint32_t alphabetSize = _alphabetNumerator[0].size();
    
    
    for (int iSequence = 0; iSequence < meas.size(); iSequence++) {
        const HmmDataMatrix_t & rawdata = meas.getMeasurements(iSequence);
        const LabelMap_t & labels = meas.getLabels(iSequence);
        const TransitionMultiMap_t & forbiddenTransitions = meas.getForbiddenTransitions(iSequence);
        
        if (rawdata.empty()) {
            continue;
        }
        
        const uint32_t numObs = rawdata[0].size();

        
        //construct alphabet probs
        HmmDataMatrix_t alphabetProbs = _alphabetNumerator;
        for (iState = 0; iState < _numStates; iState++) {
            for (iAlphabet = 0; iAlphabet < alphabetSize; iAlphabet++) {
                alphabetProbs[iState][iAlphabet] = eexp(elnproduct(_alphabetNumerator[iState][iAlphabet], -eln(_gammaCount[iState])));
            }
        }
        
        //construct transition matrix
        HmmDataMatrix_t A = _ANumerator;
        for (iState = 0; iState < _numStates; iState++) {
            for (j = 0; j < _numStates; j++) {
                A[iState][j] = eexp(elnproduct(_ANumerator[iState][j], -eln(_gammaCount[iState])));
            }
        }
        
        
        
        HmmDataMatrix_t logbmap;

        //get logbmap
        for (iState = 0; iState < _numStates; iState++) {
            HmmDataVec_t logeval;
            logeval.reserve(numObs);
            
            for (t = 0; t < numObs; t++) {
                const uint32_t idx = (uint32_t)rawdata[0][t];
                logeval.push_back(eln(alphabetProbs[iState][idx]));
            }
            
            logbmap.push_back(logeval);
        }
        
        //get forward and backward calc
        const AlphaBetaResult_t alphaBeta = HmmHelpers::getAlphaAndBeta(numObs, _pi, logbmap, A, _numStates,labels,forbiddenTransitions);
        
        
        const Hmm3DMatrix_t logxi = HmmHelpers::getLogXi(alphaBeta, logbmap,forbiddenTransitions,numObs, _numStates);
        
        
        const HmmDataMatrix_t logGamma = HmmHelpers::getLogGamma(alphaBeta, numObs, _numStates);
        
        const HmmDataMatrix_t gamma = getEEXPofMatrix(logGamma);

        HmmDataVec_t thisIterationGammaCount = getZeroedVec(_numStates);

        for (int iState = 0; iState < _numStates; iState++) {
            for (t = 0; t < numObs; t++) {
                thisIterationGammaCount[iState] += gamma[iState][t];
            }
        }
        
        HmmDataVec_t dampingVec;
        
        
        HmmDataMatrix_t ANumerator = HmmHelpers::reestimateA(A, logxi, logGamma, numObs, 1.0, min_value_for_a, _numStates);
        
        //convert to numerator by multiplying by denomenator
        // original = A/B
        // original * B = A
        for (int j = 0; j < _numStates; j++) {
            for (i = 0; i < _numStates; i++) {
                ANumerator[j][i] *= thisIterationGammaCount[j];
            }
        }
    
    
        //update numerator of A
        for (int j = 0; j < _numStates; j++) {
            for (i = 0; i < _numStates; i++) {
                _ANumerator[j][i] = elnsum(_ANumerator[j][i], eln(ANumerator[j][i]));
            }
        }
        
        
        HmmDataMatrix_t alphabetNumerator;
        for (iState = 0; iState < _numStates; iState++) {
            const HmmDataVec_t & gammaForThisState = gamma[iState];
            HmmDataVec_t alphabetForThisState = getZeroedVec(alphabetSize);
            for (t = 0; t < numObs; t++) {
                const uint32_t idx = (uint32_t)rawdata[0][t];
                alphabetForThisState[idx] += gammaForThisState[t];
            }
            
            alphabetNumerator.push_back(alphabetForThisState);
        }
        
        for (iState = 0; iState < _numStates; iState++) {
            for (j = 0; j < alphabetSize; j++) {
                _alphabetNumerator[iState][j] = elnsum(_alphabetNumerator[iState][j], eln(alphabetNumerator[iState][j]));
            }
        }
        
        //new denomenator
        for (int iState = 0; iState < _numStates; iState++) {
            _gammaCount[iState] += thisIterationGammaCount[iState];
        }

    }
}

