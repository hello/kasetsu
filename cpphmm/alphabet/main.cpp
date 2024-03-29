#include <string>
#include <iostream>
#include "DataFile.h"
#include "ModelFile.h"
#include <set>


#include <getopt.h>

#include "../src/MultiObsSequenceHiddenMarkovModel.h"
#include "../src/MatrixHelpers.h"
#include "../src/Ensemble.h"
#include "MotionSequenceForbiddenTransitions.h"

static const int32_t k_error_threshold_in_periods = 4; //each period is 5 minutes
static const int32_t priorScaleAsNumberOfSamples = 1;
static const int32_t k_num_iters_for_growing = 10;
static const int32_t k_num_iters_for_em_learning = 10;

static struct option long_options[] = {
    {"input", required_argument, 0,  0 },
    {"model",  required_argument,       0,  0},
    {"output",  required_argument, 0,  0},
    {"action",  required_argument, 0,  0},
    {"verbose",  no_argument, 0,  0},
    {"iter",  required_argument, 0,  0},
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

static MatrixMap_t getUniformInitProbabilities(const DataFile & dataFile, const uint32_t numStates, const std::string & type) {
    const MeasVec_t meas = dataFile.getMeasurements(type);
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
    bool verbose = false;
    bool useAllSequences = false;
    
    std::string input_filename;
    std::string output_filename;
    std::string model_filename;
    std::string action = "reestimate";
    
    srand (time(NULL));

    int iter = k_num_iters_for_growing;
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
                if (action == "evaluate") {
                    useAllSequences = true;
                }
            }
            else if (isOption(option_index,4)) {
                verbose = true;
            }
            else if (isOption(option_index,5)) {
                std::string value;
                value.assign(optarg);
                
                iter = atoi(value.c_str());
            }
        }
    }
    
    DataFile dataFile;
    
    if (input_filename.empty()) {
        std::cerr << "need to specify \"--input\" for measurements file" <<std::endl;
        return 1;
    }
    
    std::cout << "PARSING MEASUREMENTS FROM " << input_filename << std::endl;

    if (!dataFile.parse(input_filename,useAllSequences)) {
        std::cerr << "FAILED TO PARSE " << input_filename << std::endl;
        return 1;
    }
    
    
    HmmMap_t hmms;
    
    if (model_filename.empty()) {
        HmmDataMatrix_t A;

        
        A.resize(3);
        A[0] << 0.9999,0.0001,0.0;
        A[1] << 0.00,0.9999,0.0001;
        A[2] << 0.00,0.00,1.0;
         
        
        /*
        A.resize(2);
        A[0] << 0.50,0.50;
        A[1] << 0.50,0.50;
        */
        
        //DO SLEEP MODEL
        {
            const MeasVec_t meas = dataFile.getMeasurements(SLEEP_ENUM_STRING);
            
            MultiObsSequence multiObsSequence = getMotionSequence(meas);
            
            MatrixMap_t initAlphabetProbabilities = getUniformInitProbabilities(dataFile,A.size(),SLEEP_ENUM_STRING);
            /*
            TransitionVector_t forbiddenMotionTransitions;
            StateIdxPair noWakeUntilTwoConsecutiveMotions(LABEL_SLEEP,LABEL_POST_SLEEP);
            forbiddenMotionTransitions.push_back(noWakeUntilTwoConsecutiveMotions);
            
            UIntSet_t noMotionStates;
            noMotionStates.insert(0); //I just happen to know this
            noMotionStates.insert(1);
            */
            
            TransitionRestrictionVector_t restrictions;

            /*
            TransitionRestrictionVector_t restrictions;
            restrictions.push_back(TransitionRestrictionSharedPtr_t(new MotionSequenceForbiddenTransitions("motion",noMotionStates,forbiddenMotionTransitions)));
            */
            hmms.insert(std::make_pair(SLEEP_ENUM_STRING,
                                       MultiObsHmmSharedPtr_t(new MultiObsHiddenMarkovModel(initAlphabetProbabilities,A,restrictions))));
        }
    
        //DO BED MODEL
        {
            const MeasVec_t meas = dataFile.getMeasurements(BED_ENUM_STRING);
            
            MultiObsSequence multiObsSequence = getMotionSequence(meas);
        
            MatrixMap_t initAlphabetProbabilities = getUniformInitProbabilities(dataFile,A.size(),BED_ENUM_STRING);


/*
            TransitionVector_t forbiddenMotionTransitions;
            StateIdxPair noOutOfBed(LABEL_IN_BED,LABEL_POST_BED);
            StateIdxPair noInBed(LABEL_PRE_BED,LABEL_IN_BED);

            forbiddenMotionTransitions.push_back(noOutOfBed);
            forbiddenMotionTransitions.push_back(noInBed);

            
            UIntSet_t noMotionStates;
            noMotionStates.insert(0); //I just happen to know this
            noMotionStates.insert(1);

            TransitionRestrictionVector_t restrictions;
            restrictions.push_back(TransitionRestrictionSharedPtr_t(new MotionSequenceForbiddenTransitions("motion",noMotionStates,forbiddenMotionTransitions)));
*/
            TransitionRestrictionVector_t restrictions;

            MultiObsHiddenMarkovModel * pModel = new MultiObsHiddenMarkovModel(initAlphabetProbabilities,A,restrictions);
            
            StringSet_t motionOnly;
            motionOnly.insert("motion");
            pModel->filterModels(motionOnly);
             
            hmms.insert(std::make_pair(BED_ENUM_STRING,MultiObsHmmSharedPtr_t(pModel)));
        }

    
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
            
            const MeasVec_t meas = dataFile.getMeasurements((*it).first);
            MultiObsSequence multiObsSequence = getMotionSequence(meas);

            (*it).second->reestimate(multiObsSequence, k_num_iters_for_em_learning,priorScaleAsNumberOfSamples);
            (*it).second->evaluatePaths(multiObsSequence,k_error_threshold_in_periods,verbose);
        }
        
    }
    else if (action == "evaluate") {
        std::set<std::string> keys;
        for (auto it = hmms.begin(); it != hmms.end(); it++) {
            keys.insert((*it).first);
        }
        
        for (auto itKey = keys.begin(); itKey != keys.end(); itKey++) {
            
            std::cout << "EVALUATING " << (*itKey) << std::endl;

            const MeasVec_t meas = dataFile.getMeasurements(*itKey);
            MultiObsSequence multiObsSequence = getMotionSequence(meas);
            
            auto range = hmms.equal_range(*itKey);
            
            HmmVec_t hmmsForKey;
            for (auto it = range.first; it != range.second; it++) {
                hmmsForKey.push_back((*it).second);
            }
            
            Ensemble ensemble(hmmsForKey);

            
            ensemble.evaluate(multiObsSequence,verbose);
            
        }
        
    }
    else if (action == "grow") {
        HmmMap_t grownHmms;
        for (auto it = hmms.begin(); it != hmms.end(); it++) {
            //get seed model
            const MeasVec_t meas = dataFile.getMeasurements((*it).first);
            MultiObsSequence multiObsSequence = getMotionSequence(meas);
            
            (*it).second->reestimate(multiObsSequence, 1, priorScaleAsNumberOfSamples);
            
            //grow ensemble
            Ensemble ensemble(*(*it).second);
            ensemble.grow(multiObsSequence,iter);
            
            
            const HmmVec_t ptrs = ensemble.getModelPointers();
            
            for (auto itEnsemble = ptrs.begin(); itEnsemble != ptrs.end(); itEnsemble++) {
                grownHmms.insert(std::make_pair((*it).first,*itEnsemble));
            }
        }

        hmms = grownHmms;
    }
    else {
        std::cerr << "needed to specify action reestimate or evaluate";
        return 1;
    }
    
    if (!output_filename.empty()) {
        ModelFile::SaveProtobuf(hmms, output_filename);
        
        for (auto it = hmms.begin(); it != hmms.end(); it++) {
            MatrixMap_t mats = (*it).second->getAlphabetMatrix();
            
            for (auto imat = mats.begin(); imat != mats.end(); imat++) {
                printMat((*imat).first, (*imat).second);
            }
        }
    }
    
    return 0;
}
