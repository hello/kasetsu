#include <string>
#include <iostream>
#include "DataFile.h"
#include "ModelFile.h"

#include <getopt.h>

#include "../src/MultiObsSequenceHiddenMarkovModel.h"
#include "../src/MatrixHelpers.h"
#include "MotionSequenceForbiddenTransitions.h"

static const int32_t k_error_threshold_in_periods = 4; //each period is 5 minutes
static const int32_t priorScaleAsNumberOfSamples = 5;

static struct option long_options[] = {
    {"input", required_argument, 0,  0 },
    {"model",  required_argument,       0,  0},
    {"output",  required_argument, 0,  0},
    {"action",  required_argument, 0,  0},

    {0,         0,                 0,  0 }
};







static MultiObsSequence getMotionSequence(const MeasVec_t & meas) {
    
    MultiObsSequence seq;
    
    for (auto it = meas.begin(); it != meas.end(); it++) {
        const MatrixMap_t & ref = (*it).rawdata;
        LabelMap_t labelsCopy = (*it).labels;
        seq.addSequence(ref, labelsCopy);
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

static bool isOption(uint32_t option_index, uint32_t idx) {
    return strncmp(long_options[option_index].name,long_options[idx].name,strnlen(long_options[idx].name, 64)) == 0;
}

int main(int argc , char ** argv) {
    
    int c;
    
    std::string input_filename;
    std::string output_filename;
    std::string model_filename;
    std::string action = "reestimate";

    while (1) {
        int option_index = 0;
        
        c = getopt_long_only(argc, argv, "",long_options, &option_index);
        if (c == -1)
            break;
        
        if (c == 0) {
            if (isOption(option_index,0)) {
                input_filename.assign(optarg);
            }
            else if (isOption(option_index,1)) {
                model_filename.assign(optarg);
            }
            else if (isOption(option_index,2)) {
                output_filename.assign(optarg);
            }
            else if (isOption(option_index,3)) {
                action.assign(optarg);
            }
            
        }
    }
    
    DataFile dataFile;
    
    if (input_filename.empty()) {
        std::cerr << "need to specify \"--input\" for measurements file" <<std::endl;
        return 1;
    }
    
    std::cout << "PARSING MEASUREMENTS FROM " << input_filename << std::endl;

    if (!dataFile.parse(input_filename)) {
        std::cerr << "FAILED TO PARSE " << input_filename << std::endl;
        return 1;
    }
    
    const MeasVec_t & meas = dataFile.getMeasurements();
    
    MultiObsSequence multiObsSequence = getMotionSequence(meas);
    
    HmmMap_t hmms;
    
    if (model_filename.empty()) {
        HmmDataMatrix_t A;

        
        A.resize(3);
        A[0] << 0.9999,0.0001,0.0;
        A[1] << 0.00,0.9999,0.0001;
        A[2] << 0.00,0.00,1.0;
        
        
        /*
        A.resize(5);
        A[0] << 0.99,0.01,0.00,0.00,0.00;
        A[1] << 0.00,0.99,0.01,0.00,0.00;
        A[2] << 0.00,0.00,0.999,0.001,0.00;
        A[3] << 0.00,0.00,0.00,0.99,0.01;
        A[4] << 0.00,0.00,0.00,0.00,1.0;
*/
        
        
        MatrixMap_t initAlphabetProbabilities = getUniformInitProbabilities(dataFile,A.size());

        TransitionVector_t forbiddenMotionTransitions;
        StateIdxPair noWakeUntilTwoConsecutiveMotions(LABEL_SLEEP,LABEL_POST_SLEEP);
        forbiddenMotionTransitions.push_back(noWakeUntilTwoConsecutiveMotions);
        
        UIntSet_t noMotionStates;
        noMotionStates.insert(0); //I just happen to know this
        noMotionStates.insert(6);
        
        TransitionRestrictionVector_t restrictions;
        restrictions.push_back(new MotionSequenceForbiddenTransitions("motion",noMotionStates,forbiddenMotionTransitions));
        
        hmms.insert(std::make_pair("sleep",new MultiObsHiddenMarkovModel(initAlphabetProbabilities,A,restrictions)));
    }
    else {
        hmms = ModelFile::LoadFile(model_filename);
    }

    if (hmms.empty()) {
        std::cerr << "failed to create HMM" << std::endl;
        return 1;
    }
    
    
    if (action == "reestimate") {
        
        for (auto it = hmms.begin(); it != hmms.end(); it++) {
            std::cout << "ESTIMATING " << (*it).first << std::endl;
            (*it).second->reestimate(multiObsSequence, 1,priorScaleAsNumberOfSamples);
            (*it).second->evaluatePaths(multiObsSequence,k_error_threshold_in_periods);
        }
        
    }
    else if (action == "evaluate") {
        for (auto it = hmms.begin(); it != hmms.end(); it++) {
            std::cout << "EVALUATING " << (*it).first << std::endl;
            (*it).second->evaluatePaths(multiObsSequence,k_error_threshold_in_periods);
        }
    }
    else {
        std::cerr << "needed to specify action reestimate or evaluate";
        return 1;
    }
    
    if (!output_filename.empty()) {
        ModelFile::SaveProtobuf(hmms, output_filename);
    }
    
    for (auto it = hmms.begin(); it != hmms.end(); it++) {
        delete (*it).second;
    }

    return 0;
}
