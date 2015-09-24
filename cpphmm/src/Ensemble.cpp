#include "Ensemble.h"
#include "LogMath.h"
#include "RandomHelpers.h"
#include "MatrixHelpers.h"

#define PRIOR_WEIGHT (3.0)

typedef UNORDERED_MAP<StateIdxPair,HmmFloat_t,StateIdxPairHash> TransitionAtTimeF_t; //key is time index


Ensemble::Ensemble(const MultiObsHiddenMarkovModel & seed) {
    _models.push_back(MultiObsHmmSharedPtr_t(new MultiObsHiddenMarkovModel(seed)));
}

Ensemble::Ensemble(const HmmVec_t & hmms) {
    _models.insert(_models.begin(), hmms.begin(),hmms.end());
}

Ensemble::~Ensemble() {

}

static TransitionAtTimeF_t getTransitions(const ViterbiPath_t & path) {
    TransitionAtTimeF_t transitions;
    
    for (int t = 0; t < path.size() - 1; t++) {
        if (path[t+1] != path[t]) {
            StateIdxPair stateIdxPair(path[t],path[t+1]);
            transitions.insert(std::make_pair(stateIdxPair,t));
        }
    }
    
    return transitions;
}

static HmmFloat_t evaluateEnsembleOnData(const HmmVec_t & ensemble,const MultiObsSequence & multiObsSequence,bool verbose) {
    HmmFloat_t scoreSum = 0.0;
    uint32_t scoreCount = 0;
    
    if (ensemble.empty()) {
        std::cerr << "ENSEMBLE SIZE IS ZERO" << __FILE__ << ":" << __LINE__ << std::endl;
        return 0.0;
    }
    
    const uint32_t numStates = ensemble[0]->getNumStates();
    
    HmmDataMatrix_t confusionCount = getZeroedMatrix(numStates, numStates);
    
    for (int iMeas = 0; iMeas < multiObsSequence.size(); iMeas++) {
        
        const MultiObsSequence thisMeas = multiObsSequence.cloneOne(iMeas);
        std::vector<EvaluationResult_t> results;
        for (auto itModel = ensemble.begin(); itModel != ensemble.end(); itModel++) {
            results.push_back((*itModel)->evaluatePaths(thisMeas));
        }
        
        
        //find the best model for this measurement
        HmmFloat_t bestScore = LOGZERO;
        auto bestResult = results.end();
        for (auto it = results.begin(); it != results.end(); it++) {
            const EvaluationResult_t & ref = *it;
            
            if (ref.paths.empty()) {
                continue;
            }
            
            const HmmFloat_t score = ref.paths[0].getCost();
            
            if (score > bestScore) {
                bestScore = score;
                bestResult = it;
            }
        }
        
        if (bestResult == results.end()) {
            //wat?
            continue;
        }
        
        //add up diags of confusion matrix to get score
        const HmmDataMatrix_t bestScoringConfusionMatrix = (*bestResult).confusionMatrix;

        for (int i = 0; i < bestScoringConfusionMatrix.size(); i++) {
            scoreSum += bestScoringConfusionMatrix[i][i];
            scoreCount++;
        }

        //add counts
        const HmmDataMatrix_t bestScoringConfusionCount = (*bestResult).confusionCount;
        
        for (int j = 0; j < numStates; j++) {
            for (int i = 0; i < numStates; i++) {
                confusionCount[j][i] += bestScoringConfusionCount[j][i];
            }
        }
    }
    
    for (int j = 0; j < numStates; j++) {
        HmmFloat_t sum = 0.0;
        for (int i = 0; i < numStates; i++) {
            sum += confusionCount[j][i];
        }
        
        if (sum <= 0.0) {
            continue;
        }
        
        for (int i = 0; i < numStates; i++) {
            confusionCount[j][i] /= sum;
        }

    }

    if (verbose) {
        printMat("confusion mtx", confusionCount);
    }
    
    return scoreSum / (HmmFloat_t) scoreCount;
}

void Ensemble::evaluate(const MultiObsSequence & meas) {
    evaluateEnsembleOnData(_models,meas,true);
}


void Ensemble::grow(const MultiObsSequence & meas, uint32_t n) {
    
    HmmVec_t candidateModels;
    HmmFloat_t lastBestScore = 0.0;
    for (uint32_t iter = 0; iter < n; iter++) {
        
        //reestimate randomly
        const UIntVec_t measIndices = getBoundedRandomSeq(0,meas.size(),_models.size());
        
        int idx = 0;
        for (auto it = _models.begin(); it != _models.end(); it++) {
            
            MultiObsHmmSharedPtr_t pcopy = MultiObsHmmSharedPtr_t(new MultiObsHiddenMarkovModel(*(*it)));
            
            const MultiObsSequence seq = meas.cloneOne(measIndices[idx]);
            //choose measurement updates randomly
            
            pcopy->reestimate(seq, 1, PRIOR_WEIGHT);
            
            candidateModels.push_back(pcopy);
            
            idx++;
        }
        
        
        std::cout << "score: " << std::flush;

        //take each candidate model, add to ensemble, and try it out.
        //the candidate model with the best effect on classification accuracy gets to stay
        auto bestCandidate = candidateModels.end();
        for (auto itCandidateModel = candidateModels.begin(); itCandidateModel != candidateModels.end(); itCandidateModel++) {
            HmmVec_t testEnsemble;
            testEnsemble.insert(testEnsemble.begin(),_models.begin(),_models.end());
            testEnsemble.push_back(*itCandidateModel);
            
            const HmmFloat_t score = evaluateEnsembleOnData(testEnsemble,meas,false);
            
            std::cout << score << "," << std::flush;
            
            if (score > lastBestScore) {
                lastBestScore = score;
                bestCandidate = itCandidateModel;
            }

        }
        
        std::cout << std::endl;

    
        
        if (bestCandidate != candidateModels.end()) {
            _models.push_back(*bestCandidate);
        }
        else {
            iter--;
        }
        
        candidateModels.clear();
    
    }
}


TransitionAtTimeVec_t Ensemble::evaluatePaths(const MultiObsSequence & meas, const int32_t toleranceForError, bool verbose) const {
    std::vector<ViterbiResultVec_t> resultMatrix;
    
    //get matrix of results
    for (auto it = _models.begin(); it != _models.end(); it++) {
        const EvaluationResult_t evaluationResult = (*it)->evaluatePaths(meas, toleranceForError, verbose);
        resultMatrix.push_back(evaluationResult.paths);
    }
    
    std::vector<HmmFloat_t> costs;
    costs.resize(resultMatrix[0].size());
    for (int i = 0; i < costs.size(); i++) {
        costs[i] = LOGZERO;
    }
    
    typedef std::vector<TransitionAtTimeF_t> TransitionsByColumn_t;
    TransitionsByColumn_t transitionsByColumn;
    transitionsByColumn.resize(resultMatrix[0].size());
    
    //models go along rows, measurements go along columns
    for (size_t iRow = 0; iRow < resultMatrix.size(); iRow++) {
        const size_t numCols = resultMatrix[iRow].size();
        
        for (size_t iCol = 0; iCol < numCols; iCol++) {
            
            const ViterbiDecodeResult_t & result = resultMatrix[iRow][iCol];
            
            //cost
            const HmmFloat_t pathcost = result.getCost();
            
            //sum score for all models for this column (i.e. all the different models for this measurement)
            costs.at(iCol) = elnsum(costs.at(iCol),pathcost);

            //get predictions (transitions)
            const TransitionAtTimeF_t transitions = getTransitions(result.getPath());
            
            //weight prediction
            for (auto itTransition = transitions.begin(); itTransition != transitions.end(); itTransition++) {
                
                const HmmFloat_t t = (*itTransition).second;
                const HmmFloat_t weightedTime = elnproduct(eln(t),pathcost);
                
                const StateIdxPair & transitionIdx = (*itTransition).first;
                
                //if not populated, add
                if (transitionsByColumn[iCol].find(transitionIdx) == transitionsByColumn[iCol].end()) {
                    transitionsByColumn[iCol].insert(std::make_pair(transitionIdx,weightedTime));
                    continue;
                }
                
                
                //add to existing
                HmmFloat_t & ref = transitionsByColumn[iCol][(*itTransition).first];
                
                ref = elnsum(ref,weightedTime);
            }
        }
    }
    
    //by the time I get here, I should have all my weighted transitions, now I need to divide by the sums
    // p(o_j|model_i) * pred_i / sum_i(p(o_j|model_i))
    for (size_t iCol = 0; iCol < transitionsByColumn.size(); iCol++) {
        const HmmFloat_t logDenominator = costs[iCol];
        for (auto itTransition = transitionsByColumn[iCol].begin(); itTransition != transitionsByColumn[iCol].end(); itTransition++) {
            const HmmFloat_t logNumerator = (*itTransition).second;
            const HmmFloat_t logPrediction = elnproduct(logNumerator,-logDenominator);
            (*itTransition).second = eexp(logPrediction);
        }
    }

    //translate into ints
    TransitionAtTimeVec_t result;
    for (size_t iCol = 0; iCol < transitionsByColumn.size(); iCol++) {
        TransitionAtTime_t transitions;
        for (auto itTransition = transitionsByColumn[iCol].begin(); itTransition != transitionsByColumn[iCol].end(); itTransition++) {
            const uint32_t pred = (uint32_t)(*itTransition).second;
            const StateIdxPair key = (*itTransition).first;

            transitions.insert(std::make_pair(key,pred));
            
        }
    }
    
    return result;
    
}

HmmVec_t Ensemble::getModelPointers() const  {
    return _models;
}
