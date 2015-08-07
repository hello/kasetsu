#include <string>
#include <iostream>
#include "DataFile.h"
#include "../src/MultiObsSequenceHiddenMarkovModel.h"
#include "../src/MatrixHelpers.h"

static const char * k_filename = "1012.json";


static MultiObsSequence getMotionSequence(const MeasVec_t & meas) {
    
    MultiObsSequence seq;
    
    for (auto it = meas.begin(); it != meas.end(); it++) {
        const HmmDataMatrix_t & ref = (*it).rawdata;
        const HmmDataVec_t & vec = ref[0];
        
        
        TransitionMultiMap_t forbiddenTransitions;
        
        for (int t = 0; t < vec.size(); t++) {
            //if no motion, it is forbidden to go from sleep to wake
            if (vec[t] == 0.0 || vec[t] == 6.0) {
               forbiddenTransitions.insert(std::make_pair(t, StateIdxPair(1,0)));
            }
        }
        
        seq.addSequence(ref, forbiddenTransitions, (*it).labels);
        
        
    }
    
    return seq;
    
}

int main() {
    
    DataFile dataFile;
    
    if (dataFile.parse(k_filename)) {
        MeasVec_t meas = dataFile.getMeasurement("motion");
        const uint32_t numStates = dataFile.getNumStates("motion");
        
        HmmDataMatrix_t A;
        A.resize(2);
        A[0] << 0.99,0.01;
        A[1] << 0.01,0.99;
        
        HmmDataMatrix_t alphabet;
        alphabet.resize(2);
        alphabet[0] = getUniformVec(numStates);
        alphabet[1] = getUniformVec(numStates);
        
        
        MultiObsHiddenMarkovModel hmm(alphabet,A);
        
        hmm.reestimate(getMotionSequence(meas), 1);
    }
    
    
    return 0;
}
