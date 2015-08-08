#include <string>
#include <iostream>
#include "DataFile.h"
#include "../src/MultiObsSequenceHiddenMarkovModel.h"
#include "../src/MatrixHelpers.h"

static const char * k_filename = "1012.json";


static MultiObsSequence getMotionSequence(const MeasVec_t & meas) {
    
    MultiObsSequence seq;
    
    for (auto it = meas.begin(); it != meas.end(); it++) {
        const MatrixMap_t & ref = (*it).rawdata;
        
        auto dataIterator = ref.find("motion");
        
        const HmmDataMatrix_t & mat = (*dataIterator).second;
        const HmmDataVec_t & vec = mat[0];
        
        TransitionMultiMap_t forbiddenTransitions;
        
        for (int t = 0; t < vec.size(); t++) {
            //if no motion, it is forbidden to go from sleep to wake
            if (vec[t] == 0.0 || vec[t] == 6.0) {
                //forbiddenTransitions.insert(std::make_pair(t, StateIdxPair(1,0)));
                forbiddenTransitions.insert(std::make_pair(t, StateIdxPair(1,2)));
            }
        }
        
        seq.addSequence(ref, forbiddenTransitions, (*it).labels);
        
        
    }
    
    return seq;
    
}

static HmmDataMatrix_t getUniformAlphabetProbs(const uint32_t numStates, const uint32_t alphabetSize) {
    
    HmmDataMatrix_t alphabet;
    alphabet.resize(numStates);
    
    for (int i = 0; i < numStates; i++) {
        alphabet[i] = getUniformVec(alphabetSize);
    }

    return alphabet;
}

static MatrixMap_t getUniformInitProbabilities(const DataFile & dataFile, const uint32_t numStates) {
    const MeasVec_t & meas = dataFile.getMeasurements();
    const MatrixMap_t & rawdata = (*meas.begin()).rawdata;
    MatrixMap_t initProbsMap;
    for (auto it = rawdata.begin(); it != rawdata.end(); it++) {
        const std::string & key = (*it).first;
        
        const uint32_t alphabetSize = dataFile.getNumStates(key);
        
        initProbsMap.insert(std::make_pair(key,getUniformAlphabetProbs(numStates,alphabetSize)));
    }
    
    return initProbsMap;
}

int main() {
    
    DataFile dataFile;
    
    if (dataFile.parse(k_filename)) {
        const MeasVec_t & meas = dataFile.getMeasurements();
        
        HmmDataMatrix_t A;
        
        
        A.resize(3);
        A[0] << 0.99,0.01,0.0;
        A[1] << 0.00,0.99,0.01;
        A[2] << 0.00,0.00,1.0;
        
        
        /*
        A.resize(2);
        A[0] << 0.99,0.01;
        A[1] << 0.01,0.99;
        */
        
        MatrixMap_t initAlphabetProbabilities = getUniformInitProbabilities(dataFile,A.size());
        MultiObsHiddenMarkovModel hmm(initAlphabetProbabilities,A);
        MultiObsSequence multiObsSequence = getMotionSequence(meas);
        hmm.reestimate(multiObsSequence, 20);
    }
    
    
    return 0;
}
