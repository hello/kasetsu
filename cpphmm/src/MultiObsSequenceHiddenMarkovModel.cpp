#include "MultiObsSequenceHiddenMarkovModel.h"
#include "CompositeModel.h"
#include "HmmHelpers.h"
#include "MatrixHelpers.h"
#include "ThreadPool.h"
#include "LogMath.h"
#include <assert.h>

#define MIN_A (1e-6)
#define MIN_PROB (1e-6)

MultiObsHiddenMarkovModel::MultiObsHiddenMarkovModel(const MatrixMap_t & initialAlphabetProbs,const HmmDataMatrix_t & A) {
    
    _numStates = A.size();
    _logDenominator.reserve(_numStates);
    
    for (int i = 0; i < _numStates; i++) {
        _logDenominator.push_back(0.0);
    }
    
    for (auto it = initialAlphabetProbs.begin(); it != initialAlphabetProbs.end();it++) {
        _alphabetNumerator[(*it).first] = getELNofMatrix((*it).second);
    }
    
    
    _ANumerator = getELNofMatrix(A);
    _pi = getZeroedVec(_numStates);
    _pi[0] = 1.0;
}

MultiObsHiddenMarkovModel::~MultiObsHiddenMarkovModel() {
    
}




HmmDataMatrix_t MultiObsHiddenMarkovModel::getAMatrix() const {
    //construct transition matrix
    HmmDataMatrix_t A = _ANumerator;
    for (int iState = 0; iState < _numStates; iState++) {
        for (int j = 0; j < _numStates; j++) {
            A[iState][j] = eexp(elnproduct(_ANumerator[iState][j], -_logDenominator[iState]));
            
            if (A[iState][j] < MIN_A && A[iState][j] != 0.0) {
                A[iState][j] = MIN_A;
            }
        }
        
        HmmFloat_t thesum = 0.0;
        for (int j = 0; j < _numStates; j++) {
            thesum += A[iState][j];
        }
        
        for (int j = 0; j < _numStates; j++) {
            A[iState][j] /= thesum;
        }
        
    }
    
    
    
    return A;
}

MatrixMap_t MultiObsHiddenMarkovModel::getAlphabetMatrix() const {
    
    MatrixMap_t alphabetProbsMap;
    int iState;
    
    for (MatrixMap_t::const_iterator it = _alphabetNumerator.begin(); it != _alphabetNumerator.end(); it++) {
        HmmDataMatrix_t numerator = (*it).second;
        std::string key = (*it).first;
        
        if (numerator.empty()) {
            continue;
        }
        
        const uint32_t alphabetSize = numerator[0].size();
                
        //construct alphabet probs
        HmmDataMatrix_t alphabetProbs = numerator;
        for (iState = 0; iState < _numStates; iState++) {
            for (int iAlphabet = 0; iAlphabet < alphabetSize; iAlphabet++) {
                const HmmFloat_t value = eexp(elnproduct(numerator[iState][iAlphabet], -_logDenominator[iState]));

                alphabetProbs[iState][iAlphabet] = value;
                
                if (alphabetProbs[iState][iAlphabet] < MIN_PROB) {
                    alphabetProbs[iState][iAlphabet] = MIN_PROB;
                }
            }
            
            HmmFloat_t thesum = 0.0;
            for (int iAlphabet = 0; iAlphabet < alphabetSize; iAlphabet++) {
                thesum += alphabetProbs[iState][iAlphabet];
            }
            
            for (int iAlphabet = 0; iAlphabet < alphabetSize; iAlphabet++) {
                alphabetProbs[iState][iAlphabet] /= thesum;
            }

        }
        
        alphabetProbsMap.insert(std::make_pair(key, alphabetProbs));
    }
    
    return alphabetProbsMap;
}

HmmDataMatrix_t MultiObsHiddenMarkovModel::getLogBMap(const MatrixMap_t & rawdataMap, const MatrixMap_t & alphabetProbsMap) const {
    HmmDataMatrix_t logbmap;
    
    
    if (rawdataMap.empty()) {
        return logbmap;
    }
    
    
    const uint32_t numObs = (*rawdataMap.begin()).second[0].size();
    
    logbmap = getZeroedMatrix(_numStates, numObs);
    
    for (auto it = alphabetProbsMap.begin(); it != alphabetProbsMap.end(); it++) {
        const std::string & key = (*it).first;
        const HmmDataMatrix_t & alphabetProbs = (*it).second;
         
        auto rawDataIt = rawdataMap.find(key);
        
        if (rawDataIt == rawdataMap.end()) {
            std::cerr << "could not find " << key << " in raw data map" << std::endl;
            continue;
        }
        
        const HmmDataMatrix_t & rawdata = (*rawDataIt).second;
        
        
        //get logbmap
        for (int iState = 0; iState < _numStates; iState++) {
            for (int t = 0; t < numObs; t++) {
                const uint32_t idx = (uint32_t)rawdata[0][t];
                
                assert(idx >= 0 && idx < alphabetProbs[0].size());
                
                logbmap[iState][t] = elnproduct(logbmap[iState][t], eln(alphabetProbs[iState][idx]));
            }
        }
    }
    
    return logbmap;
}

/*
static UIntVec_t getVecFromLabels(const LabelMap_t & labels, const uint32_t end,const uint32_t nolabellabel) {
    UIntVec_t vec;
    vec.reserve(end);
    for (uint32_t t = 0; t < end; t++) {
        LabelMap_t::const_iterator it = labels.find(t);
        
        if (it != labels.end()) {
            vec.push_back((*it).second);
        }
        else {
            vec.push_back(nolabellabel);
        }
    }
    
    return vec;
}
*/
static void evalLabels(const LabelMap_t & labels,const ViterbiPath_t & path,HmmDataMatrix_t & confusionMatrix) {
    
    for (uint32_t t = 0; t < path.size(); t++) {
        LabelMap_t::const_iterator it = labels.find(t);
        
        if (it != labels.end()) {
            uint32_t label = (*it).second;
            uint32_t prediction = path[t];
            
            confusionMatrix[prediction][label] += 1.0;
        }
        
        
    }
    
    
}


void MultiObsHiddenMarkovModel::reestimate(const MultiObsSequence & meas,const uint32_t numIter) {
    int iterationNumber,iSequence;
    
    for (iterationNumber = 0; iterationNumber < numIter; iterationNumber++) {
        for (iSequence = 0; iSequence < meas.size(); iSequence++) {
            const MatrixMap_t & rawdata = meas.getMeasurements(iSequence);
            const LabelMap_t & labels = meas.getLabels(iSequence);
            const TransitionMultiMap_t & forbiddenTransitions = meas.getForbiddenTransitions(iSequence);
            
            if (rawdata.empty()) {
                continue;
            }
            
            if (iSequence % 100 == 0)
                std::cout << "SEQUENCE " <<iSequence << std::endl;
            
            const uint32_t numObs = (*rawdata.begin()).second[0].size();
            
            const MatrixMap_t alphabetProbsMap = getAlphabetMatrix();
            
            const HmmDataMatrix_t A = getAMatrix();
            
            const HmmDataMatrix_t logbmap = getLogBMap(rawdata,alphabetProbsMap);
            
            const AlphaBetaResult_t alphaBeta = HmmHelpers::getAlphaAndBeta(numObs, _pi, logbmap, A, _numStates,labels,forbiddenTransitions);
            
            const HmmDataMatrix_t logANumerator = HmmHelpers::getLogANumerator(A,alphaBeta, logbmap, forbiddenTransitions, numObs, _numStates);
            
            const HmmDataVec_t logDenominator = HmmHelpers::getLogDenominator(alphaBeta, _numStates, numObs);
            
            if (iSequence == 0) {
                _ANumerator = logANumerator;
                _logDenominator = logDenominator;
            }
            else {
                _ANumerator = HmmHelpers::elnAddMatrix(_ANumerator, logANumerator);
                _logDenominator = HmmHelpers::elnAddVector(_logDenominator, logDenominator);
            }

            
            for (MatrixMap_t::const_iterator it = rawdata.begin(); it != rawdata.end(); it++) {
                const std::string & key = (*it).first;

                assert(_alphabetNumerator.find(key) != _alphabetNumerator.end());
                
                const uint32_t alphabetSize = _alphabetNumerator[key][0].size();
                const HmmDataMatrix_t logAlphabetNumerator = HmmHelpers::getLogAlphabetNumerator(alphaBeta, (*it).second[0], _numStates, numObs, alphabetSize);
                
                if (iSequence == 0) {
                    _alphabetNumerator[key] = logAlphabetNumerator;

                }
                else {
                    _alphabetNumerator[key] = HmmHelpers::elnAddMatrix(_alphabetNumerator[key], logAlphabetNumerator);
                }
                
            }
        }
    
    
        
        printMat("A", getAMatrix(),4);
        std::cout << std::endl;
        
        const MatrixMap_t alphabetProbsMap = getAlphabetMatrix();
        
        for (auto it = alphabetProbsMap.begin(); it != alphabetProbsMap.end(); it++) {
            printMat((*it).first, (*it).second);
            std::cout << std::endl;
        }
        
        
        HmmDataMatrix_t confusionMatrix = getZeroedMatrix(_numStates,_numStates);
        
        for (iSequence = 0; iSequence < meas.size(); iSequence++) {
            const MatrixMap_t & rawdata = meas.getMeasurements(iSequence);
            const LabelMap_t & labels = meas.getLabels(iSequence);
            const TransitionMultiMap_t & forbiddenTransitions = meas.getForbiddenTransitions(iSequence);
            const uint32_t numObs = (*rawdata.begin()).second[0].size();
            
            ViterbiDecodeResult_t decodedResult = HmmHelpers::decodeWithoutLabels(getAMatrix(), getLogBMap(rawdata, getAlphabetMatrix()), _pi, forbiddenTransitions, _numStates, numObs);
            
            
            evalLabels(labels,decodedResult.getPath(),confusionMatrix);
            
            /*
             const UIntVec_t v = getVecFromLabels(labels,numObs,3);
             
             int foo = 3;
             std::cout << "path = [" << decodedResult.getPath() << "]" << std::endl;
             std::cout << "meas = [" << (*rawdata.find("motion")).second[0] << "]" << std::endl;
             std::cout << "labels = [" << v << "]" << std::endl;
             std::cout << "meas2 = [" << (*rawdata.find("light2")).second[0] << "]" << std::endl;
             
             foo++;
             */
            
        }
        
        for (int i = 0; i < _numStates; i++) {
            HmmFloat_t thesum = 0.0;
            for (int j = 0; j < _numStates; j++) {
                thesum += confusionMatrix[i][j];
            }
            
            for (int j = 0; j < _numStates; j++) {
                confusionMatrix[i][j] /= thesum;
            }
        }
        
        printMat("CONFUSION", confusionMatrix);
        
    }
}

