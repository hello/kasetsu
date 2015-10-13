#include "MultiObsSequenceHiddenMarkovModel.h"
#include "CompositeModel.h"
#include "HmmHelpers.h"
#include "MatrixHelpers.h"
#include "ThreadPool.h"
#include "LogMath.h"
#include <assert.h>
#include <stdio.h>

#define MIN_A (1e-6)
#define MIN_PROB (1e-6)

#define PRIOR_STRENGTH (1e-50)

#define SLEEP_STATE (1) 
#define SLEEP_STATE_MIN_DURATION (1)


MultiObsHiddenMarkovModel::MultiObsHiddenMarkovModel(const MatrixMap_t & initialAlphabetProbs,const HmmDataMatrix_t & A,TransitionRestrictionVector_t forbiddenTransitions) {
    _A = A;
    _numStates = A.size();
    _logDenominator.reserve(_numStates);
    
    for (int i = 0; i < _numStates; i++) {
        _logDenominator.push_back(eln(PRIOR_STRENGTH));
    }
    
    for (auto it = initialAlphabetProbs.begin(); it != initialAlphabetProbs.end();it++) {
        _logAlphabetNumerator[(*it).first] = HmmHelpers::elnMatrixScalarProduct(getELNofMatrix((*it).second),PRIOR_STRENGTH);
    }
    
    
    _logANumerator = HmmHelpers::elnMatrixScalarProduct(getELNofMatrix(A),PRIOR_STRENGTH);
    
    _pi = getZeroedVec(_numStates);
    _pi[0] = 1.0;
    
    
    printMat("original A", getAMatrix());
    
    _forbiddenTransitions = forbiddenTransitions;
    
}

MultiObsHiddenMarkovModel::MultiObsHiddenMarkovModel(const MatrixMap_t & logAlphabetNumerator,const HmmDataMatrix_t & logANumerator, const HmmDataVec_t & logDenominator, TransitionRestrictionVector_t forbiddenTransitions,const HmmFloat_t scalingFactor) {
    
    _logANumerator = logANumerator;
    _numStates = _logANumerator.size();

    _logDenominator = logDenominator;
    _logAlphabetNumerator = logAlphabetNumerator;
    
    
    scale(scalingFactor);
        
    _A = getAMatrix();
    
    _pi = getZeroedVec(_numStates);
    _pi[0] = 1.0;
    
    _forbiddenTransitions = forbiddenTransitions;


}


MultiObsHiddenMarkovModel::~MultiObsHiddenMarkovModel() {
   
}

void MultiObsHiddenMarkovModel::scale(const HmmFloat_t scaleFactor) {
    for (auto it = _logAlphabetNumerator.begin(); it != _logAlphabetNumerator.end();it++) {
        (*it).second = HmmHelpers::elnMatrixScalarProduct((*it).second,scaleFactor);
    }
    
    _logANumerator = HmmHelpers::elnMatrixScalarProduct(_logANumerator,scaleFactor);
    _logDenominator = HmmHelpers::elnVectorScalarProduct(_logDenominator,scaleFactor);
}






HmmDataMatrix_t MultiObsHiddenMarkovModel::getAMatrix() const {
    //construct transition matrix
    HmmDataMatrix_t A = _logANumerator;
    for (int iState = 0; iState < _numStates; iState++) {
        for (int j = 0; j < _numStates; j++) {
            A[iState][j] = eexp(elnproduct(_logANumerator[iState][j], -_logDenominator[iState]));
            
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
    
    
    (void)A;
    return A;
}

MatrixMap_t MultiObsHiddenMarkovModel::getAlphabetMatrix() const {
    
    MatrixMap_t alphabetProbsMap;
    int iState;
    
    for (MatrixMap_t::const_iterator it = _logAlphabetNumerator.begin(); it != _logAlphabetNumerator.end(); it++) {
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




void MultiObsHiddenMarkovModel::reestimate(const MultiObsSequence & meas,const uint32_t numIter, const HmmFloat_t priorWeightAsNumberOfSamples) {
    int iterationNumber,iSequence;
    
    for (iterationNumber = 0; iterationNumber < numIter; iterationNumber++) {
        uint32_t numRecordsProcessed = 0;
        uint32_t numFuckedRecords = 0;

        for (iSequence = 0; iSequence < meas.size(); iSequence++) {
            const MatrixMap_t & rawdata = meas.getMeasurements(iSequence);
            const LabelMap_t & labels = meas.getLabels(iSequence);
            const TransitionMultiMap_t forbiddenTransitions = getForbiddenTransitions(rawdata);
            
            if (rawdata.empty()) {
                continue;
            }
            
            if (labels.empty()) {
                continue;
            }
            
            if (iSequence - 1 % 100 == 0)
                std::cout << "SEQUENCE " <<iSequence << std::endl;
            
            const uint32_t numObs = (*rawdata.begin()).second[0].size();
            
            const MatrixMap_t alphabetProbsMap = getAlphabetMatrix();
            
            const HmmDataMatrix_t A = getAMatrix();
            
            const HmmDataMatrix_t logbmap = getLogBMap(rawdata,alphabetProbsMap);
            
            const AlphaBetaResult_t alphaBeta = HmmHelpers::getAlphaAndBeta(numObs, _pi, logbmap, A, _numStates,labels,forbiddenTransitions);
            
            const HmmDataMatrix_t logANumerator = HmmHelpers::getLogANumerator(A,alphaBeta, logbmap, forbiddenTransitions, numObs, _numStates);
            
            const HmmDataVec_t logDenominator = HmmHelpers::getLogDenominator(alphaBeta, _numStates, numObs);
            
            bool isFucked = false;
            for (auto it = logDenominator.begin(); it != logDenominator.end(); it++) {
                if ((*it) == LOGZERO){
                    isFucked = true;
                }
            }
            
            if (isFucked) {
                numFuckedRecords++;
                continue;
            }
            
            
            _logANumerator = HmmHelpers::elnAddMatrix(_logANumerator, logANumerator);
            _logDenominator = HmmHelpers::elnAddVector(_logDenominator, logDenominator);
          

            
            for (MatrixMap_t::const_iterator it = rawdata.begin(); it != rawdata.end(); it++) {
                const std::string & key = (*it).first;

                if(_logAlphabetNumerator.find(key) == _logAlphabetNumerator.end()) {
                    continue;
                }
                
                const uint32_t alphabetSize = _logAlphabetNumerator[key][0].size();
                const HmmDataMatrix_t logAlphabetNumerator = HmmHelpers::getLogAlphabetNumerator(alphaBeta, (*it).second[0], _numStates, numObs, alphabetSize);
                
                
                _logAlphabetNumerator[key] = HmmHelpers::elnAddMatrix(_logAlphabetNumerator[key], logAlphabetNumerator);
                
                
            }
            
            numRecordsProcessed++;
        }
    
        if (numFuckedRecords > 0) {
            std::cout << "SKIPPED " << numFuckedRecords << " RECORDS OUT OF " << numRecordsProcessed + numFuckedRecords << " TOTAL" << std::endl;
        }
        
        if (priorWeightAsNumberOfSamples > 0) {
            const HmmFloat_t scaleFactor = (HmmFloat_t)priorWeightAsNumberOfSamples / (HmmFloat_t)numRecordsProcessed;
            
            scale(scaleFactor);
        }
        
        /*
        printMat("A", getAMatrix(),2);
        std::cout << std::endl;
        
        
        const MatrixMap_t alphabetProbsMap = getAlphabetMatrix();
        
        for (auto it = alphabetProbsMap.begin(); it != alphabetProbsMap.end(); it++) {
            printMat((*it).first, (*it).second);
            std::cout << std::endl;
        }
        */
    }
}


const HmmDataVec_t & MultiObsHiddenMarkovModel::getPi() const {
    return _pi;
}

const MatrixMap_t & MultiObsHiddenMarkovModel::getLogAlphabetNumerator() const {
    return _logAlphabetNumerator;
}
const HmmDataVec_t & MultiObsHiddenMarkovModel::getLogDenominator() const {
    return _logDenominator;
}

const HmmDataMatrix_t & MultiObsHiddenMarkovModel::getLogANumerator() const {
    return _logANumerator;
}

uint32_t MultiObsHiddenMarkovModel::getNumStates() const {
    return _numStates;
}

UIntVec_t MultiObsHiddenMarkovModel::getMinStatedDurations() const {
    UIntVec_t minDurations;
    minDurations.reserve(_numStates);
    for (int i = 0; i < _numStates; i++) {
        minDurations.push_back(1);
    }
    
    minDurations[SLEEP_STATE] = SLEEP_STATE_MIN_DURATION;
    
    return minDurations;
}


const TransitionRestrictionVector_t & MultiObsHiddenMarkovModel::getTransitionRestrictions() const  {
    return _forbiddenTransitions;
}



EvaluationResult_t MultiObsHiddenMarkovModel::evaluatePaths(const MultiObsSequence & meas, const int32_t toleranceForError,bool verbose)  const {
    uint32_t failCount = 0;
    uint32_t successCount = 0;
    ViterbiResultVec_t results;
    HmmDataMatrix_t confusionMatrix = getZeroedMatrix(_numStates,_numStates);

    TransitionAtTime_t totalErrorCount;
    TransitionAtTime_t totalLabelCount;
    
    const UIntVec_t minDurations = getMinStatedDurations();
   
    
    for (uint32_t iSequence = 0; iSequence < meas.size(); iSequence++) {
        const MatrixMap_t & rawdata = meas.getMeasurements(iSequence);
        const LabelMap_t & labels = meas.getLabels(iSequence);
        const TransitionMultiMap_t forbiddenTransitions = getForbiddenTransitions(rawdata);
        const uint32_t numObs = (*rawdata.begin()).second[0].size();

        /*
        if (iSequence != 1) {
            continue;
        }
         */
        
        /*
        for (auto it = rawdata.begin(); it != rawdata.end(); it++) {
            printVec((*it).first, (*it).second[0]);
        }
         */
        
        ViterbiDecodeResult_t result = HmmHelpers::decodeWithMinimumDurationConstraints(getAMatrix(), getLogBMap(rawdata, getAlphabetMatrix()), _pi, forbiddenTransitions,minDurations, _numStates, numObs);
        
        if (verbose) {
            std::cout << "COST: " << result.getCost() << std::endl;
            HmmHelpers::printTransitions(result.getPath());
        }
        
        HmmHelpers::updateConfusionCount(labels, result.getPath(), confusionMatrix);
        
        const TransitionAtTime_t matchedTransitions = HmmHelpers::evalLabels(totalLabelCount,labels,result.getPath());
        
        
        
        for (auto it = matchedTransitions.begin(); it != matchedTransitions.end(); it++) {
            const int32_t error = (*it).second;
            
            if (abs(error) > toleranceForError) {
                auto it2 = totalErrorCount.find((*it).first);
                
                if (it2 == totalErrorCount.end()) {
                    totalErrorCount.insert(std::make_pair((*it).first,0));
                }
                
                totalErrorCount[(*it).first] += 1;
                failCount++;

            }
            else {
                successCount++;
            }
            
            
            //std::cout << (*it).first.from << "," << (*it).first.to << "," << (*it).second << std::endl;
        }
        
        
        results.push_back(result);
    }
    
    const HmmDataMatrix_t confusionCount = confusionMatrix;
    for (int i = 0; i < _numStates; i++) {
        HmmFloat_t thesum = 0.0;
        for (int j = 0; j < _numStates; j++) {
            thesum += confusionMatrix[i][j];
        }
        
        if (thesum > 0) {
            for (int j = 0; j < _numStates; j++) {
                confusionMatrix[i][j] /= thesum;
            }
        }
    }
    
    if (verbose) {
        std::cout << "THERE ARE " << successCount << " SUCCESSFUL LABELS OUT OF " << successCount + failCount << " TOTAL"<< std::endl;
        std::cout << std::endl;
        if (!totalErrorCount.empty()) {
            std::cout << "HERE ARE THE BAD PREDICTIONS" << std::endl;
            for (auto it = totalErrorCount.begin(); it != totalErrorCount.end(); it++) {
                const uint32_t fromState = (*it).first.from;
                const uint32_t toState = (*it).first.to;
                const int32_t errorCount = (*it).second;
                const int32_t labelCount = totalLabelCount[(*it).first];
                std::cout << "transition: " << fromState << " --> " << toState
                << ", errors: " << errorCount
                << ", out of #labels: " << labelCount
                << ", success frac = " << 1.0 - (float)errorCount / (float) labelCount
                << std::endl << std::endl;
                
                
            }
        }
        
        printMat("CONFUSION (BY PERIODS)", confusionMatrix);
    }
    EvaluationResult_t evaluationResult;
    evaluationResult.paths = results;
    evaluationResult.confusionMatrix = confusionMatrix;
    evaluationResult.confusionCount = confusionCount;
    
    return evaluationResult;
}

TransitionMultiMap_t MultiObsHiddenMarkovModel::getForbiddenTransitions(const MatrixMap_t & measurements) const {
    
    TransitionMultiMap_t all;
    
    for (auto it = _forbiddenTransitions.begin(); it != _forbiddenTransitions.end(); it++) {
        const  TransitionMultiMap_t forbiddenTransitions = (*it)->getTimeIndexedRestrictions(measurements);
        all.insert(forbiddenTransitions.begin(), forbiddenTransitions.end());
    }
    
    return all;
    
}

void MultiObsHiddenMarkovModel::filterModels(const StringSet_t & filterKeys) {
    MatrixMap_t keptModels;
    
    for (auto it = _logAlphabetNumerator.begin(); it != _logAlphabetNumerator.end(); it++) {
        if  ( filterKeys.find((*it).first) == filterKeys.end()) {
            continue;
        }
        
        //found a keeper
        keptModels.insert(std::make_pair((*it).first,(*it).second));
    }
    
    _logAlphabetNumerator = keptModels;
}


