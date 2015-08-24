#include "ModelFile.h"
#include <rapidjson/document.h>
#include <rapidjson/rapidjson.h>
#include <rapidjson/stringbuffer.h>
#include <rapidjson/writer.h>
#include <fstream>
#include <assert.h>
#include "online_hmm.pb.h"

/*
#define LOG_A_NUMERATOR           "log_a_numerator"
#define LOG_ALPHABET_NUMERATOR    "log_alphabet_numerator"
#define LOG_DENOMINATOR           "log_denominator"

using namespace rapidjson;

static Value encodeVector(Document & d, const HmmDataVec_t & vec) {
    Value array;
    array.SetArray();
    const int n = vec.size();
    for (int i = 0; i < n; i++) {
        array.PushBack(vec[i], d.GetAllocator());
    }
    
    return array;

}

static Value encodeMatrix(Document & d,const HmmDataMatrix_t & mtx) {
    
    Value arrayOfArrays;
    arrayOfArrays.SetArray();
    
    const int m = mtx.size();
    
    for (int j = 0; j < m; j++) {
        arrayOfArrays.PushBack(encodeVector(d,mtx[j]), d.GetAllocator());
    }
    

    return arrayOfArrays;
}

static HmmDataVec_t decodeVector(Value::ConstValueIterator vecbegin, Value::ConstValueIterator vecend) {
    HmmDataVec_t vec;
    vec.reserve(1024);
    for (Value::ConstValueIterator it = vecbegin;
         it != vecend; it++) {
        
        vec.push_back((*it).GetDouble());
    }

    return vec;
}

static HmmDataMatrix_t decodeMatrix(Value::ConstValueIterator mtxbegin, Value::ConstValueIterator mtxend) {
    
    HmmDataMatrix_t mtx;
    
    for (Value::ConstValueIterator rowiterator = mtxbegin; rowiterator != mtxend; rowiterator++) {
        mtx.push_back(decodeVector((*rowiterator).Begin(),(*rowiterator).End()));
    }
    
    
    return mtx;
}



HmmMap_t * ModelFile::LoadFile(const std::string & filename) {
    std::ifstream file(filename.c_str());
    
    if (!file.is_open()) {
        return NULL;
    }
    
    file.seekg(0,std::ios::end);
    std::string str;
    str.reserve(file.tellg());
    file.seekg(0, std::ios::beg);
    
    str.assign((std::istreambuf_iterator<char>(file)),
               std::istreambuf_iterator<char>());
    
    Document d;
    d.Parse(str.c_str());
    

    for (Value::ConstMemberIterator it = d.MemberBegin(); it != d.MemberEnd(); it++) {
        std::cout << (*it).name.GetString() << std::endl;
    }
    
    
    assert(d.IsObject());
    
    const HmmDataMatrix_t logANumerator = decodeMatrix(d[LOG_A_NUMERATOR].Begin(),d[LOG_A_NUMERATOR].End());
    const HmmDataVec_t logDenominator = decodeVector(d[LOG_DENOMINATOR].Begin(),d[LOG_DENOMINATOR].End());
    
    MatrixMap_t logAlphabetNumerator;
    
    for (Value::ConstMemberIterator it = d[LOG_ALPHABET_NUMERATOR].MemberBegin();
         it != d[LOG_ALPHABET_NUMERATOR].MemberEnd(); it++) {
        
        const HmmDataMatrix_t mtx = decodeMatrix((*it).value.Begin(),(*it).value.End());
        const std::string key = (*it).name.GetString();
        logAlphabetNumerator.insert(std::make_pair(key, mtx));
        
    }
    
    if (logAlphabetNumerator.empty()) {
        return NULL;
    }
    
    if (logANumerator.empty()) {
        return NULL;
    }
    
    if (logDenominator.empty()) {
        return NULL;
    }
    
    std::cout << "successfully deserialized all the data... " << std::endl;
    
    return new MultiObsHiddenMarkovModel(logAlphabetNumerator,logANumerator,logDenominator);
}
 */

/*
void ModelFile::SaveFile(const HmmMap_t &hmms,const std::string & filename) {
    Document d;
    StringBuffer buffer;
    
    Writer<StringBuffer> writer(buffer);
    
    d.SetObject();
    
    const MatrixMap_t & alphabets = hmm.getLogAlphabetNumerator();
    
    Value alphabetObj;
    alphabetObj.SetObject();
    
    for (MatrixMap_t::const_iterator it = alphabets.begin(); it != alphabets.end(); it++) {
        const std::string & key = (*it).first;
        const HmmDataMatrix_t & mat = (*it).second;
        
        Value name;
        name.SetString(key.c_str(),key.size());
        alphabetObj.AddMember(name,encodeMatrix(d, mat),d.GetAllocator());
    }
    

    d.AddMember("confusion",encodeMatrix(d,hmm.getLastConfusionMatrix()),d.GetAllocator());

    d.AddMember(LOG_A_NUMERATOR,encodeMatrix(d,hmm.getLogANumerator()),d.GetAllocator());
    d.AddMember(LOG_ALPHABET_NUMERATOR,alphabetObj,d.GetAllocator());
    d.AddMember(LOG_DENOMINATOR,encodeVector(d, hmm.getLogDenominator()),d.GetAllocator());

    d.Accept(writer);
    
    std::ofstream outfile(filename);
    
    outfile << buffer.GetString();
    

}
 */

static hello::RealMatrix matrixFromMatrix(const HmmDataMatrix_t & mtx) {
    hello::RealMatrix mtx2;
    mtx2.set_num_rows(mtx.size());
    mtx2.set_num_cols(mtx[0].size());
    
    for (int j = 0; j < mtx.size(); j++) {
        for (int i = 0; i < mtx[0].size(); i++) {
            mtx2.add_data(mtx[j][i]);
        }
    }
    
    return mtx2;
}


static HmmDataMatrix_t getMatFromRealMatrix(const hello::RealMatrix & realmat) {
    HmmDataMatrix_t mtx;
    mtx.resize(realmat.num_rows());
    
    int k = 0;
    for (int j = 0; j < mtx.size(); j++) {
        mtx[j].resize(realmat.num_cols());
        
        for (int i = 0; i < realmat.num_cols(); i++) {
            mtx[j][i] = realmat.data(k++);
        }
    }
    
    return mtx;
}

static std::pair<std::string,MultiObsHiddenMarkovModel *> hmmFromPrior(const hello::AlphabetHmmPrior & prior,const std::string & outputId, const TransitionVector_t & forbiddenMotiontransitions) {
    /*
    optional string id = 1;
    optional OutputId output_id = 2;
    optional int64 date_created_utc = 3;
    optional int64 date_updated_utc = 4;
    optional RealMatrix log_state_transition_numerator = 5;
    repeated RealMatrix log_observation_model_numerator = 6;
    repeated string log_observation_model_ids = 7;
    repeated double log_denominator = 8;
    repeated double pi = 9;
    repeated int32 end_states = 10;
    repeated int32 minimum_state_durations = 11;
     
     const MatrixMap_t & logAlphabetNumerator,const HmmDataMatrix_t & logANumerator, const HmmDataVec_t & logDenominator,const HmmFloat_t scalingFactor = 1.0
     */
    
    
    assert(prior.has_log_state_transition_numerator());
    assert(prior.has_output_id());
    assert(prior.log_denominator_size() > 0);
    assert(prior.log_observation_model_ids_size() > 0);
    assert(prior.log_observation_model_numerator_size() > 0);
    
    MatrixMap_t logAlphabetNumerator;
    
    for (int i = 0; i < prior.log_observation_model_ids_size(); i++) {
        std::string modelId = prior.log_observation_model_ids(i);
        hello::RealMatrix mtx = prior.log_observation_model_numerator(i);
        logAlphabetNumerator.insert(std::make_pair(modelId,getMatFromRealMatrix(mtx)));
    }
    
    HmmDataMatrix_t logANumerator = getMatFromRealMatrix(prior.log_state_transition_numerator());
    
    HmmDataVec_t logDenominator;
    logDenominator.reserve(prior.log_denominator_size());
    
    for (int i = 0; i < prior.log_denominator_size(); i++) {
        logDenominator.push_back(prior.log_denominator(i));
    }
    
    
    
    return std::make_pair(outputId,new MultiObsHiddenMarkovModel(logAlphabetNumerator,logANumerator,logDenominator,forbiddenMotiontransitions));
    
}

HmmMap_t ModelFile::LoadFile(const std::string & filename) {
    HmmMap_t hmms;
    
    std::ifstream file(filename.c_str());
    
    if (!file.is_open()) {
        return hmms;
    }
    
    file.seekg(0,std::ios::end);
    std::string str;
    str.reserve(file.tellg());
    file.seekg(0, std::ios::beg);
    
    str.assign((std::istreambuf_iterator<char>(file)),
               std::istreambuf_iterator<char>());

    hello::AlphabetHmmUserModel protobuf;
    protobuf.ParseFromString(str);
    
    for (int iModel = 0; iModel < protobuf.models_size(); iModel++) {
        hello::AlphabetHmmPrior prior = protobuf.models(iModel);
        
        std::string outputId;
        
        switch (prior.output_id()) {
            case hello::SLEEP:
            {
                outputId = "sleep";
                break;
            }
                
            case hello::BED:
            {
                outputId = "bed";
                break;
            }
                
            default:
            {
                assert(false && "NOT A VALID ENUMERATION FOR OUTPUT ID");
            }
        }
        
        TransitionVector_t forbiddenMotionTransitions;
        
        for (int i = 0; i < protobuf.forbiddeden_motion_transitions_size(); i++) {
            hello::Transition transition = protobuf.forbiddeden_motion_transitions(i);
            
            if (transition.output_id() == outputId) {
                StateIdxPair t(transition.from(),transition.to());
                forbiddenMotionTransitions.push_back(t);
            }
            
        }

        
        hmms.insert(hmmFromPrior(prior,outputId,forbiddenMotionTransitions));
        
    }
    
    
    
    return hmms;
}


void ModelFile::SaveProtobuf(const HmmMap_t &hmms, const std::string &filename) {
    
    hello::AlphabetHmmUserModel model;
    
    for (auto hmmIterator = hmms.begin(); hmmIterator != hmms.end(); hmmIterator++) {
        hello::AlphabetHmmPrior * prior = model.add_models();


        const MultiObsHiddenMarkovModel & hmm = *((*hmmIterator).second);
        const std::string & outputId = (*hmmIterator).first;
        
        prior->set_id("default");
        
        if (outputId == "sleep") {
            prior->set_output_id(hello::OutputId::SLEEP);
        }
        else if (outputId == "bed") {
            prior->set_output_id(hello::OutputId::BED);
        }
        else {
            assert(false && "output id was not sleep or bed");
        }
        
        prior->set_date_created_utc(0);
        prior->set_date_updated_utc(0);
        
        for (auto it = hmm.getLogAlphabetNumerator().begin(); it != hmm.getLogAlphabetNumerator().end(); it++) {
            prior->add_log_observation_model_ids((*it).first);
            *(prior->add_log_observation_model_numerator()) = matrixFromMatrix((*it).second); //hope this works
        }
        
        for (int i = 0; i < hmm.getLogDenominator().size(); i++) {
            prior->add_log_denominator(hmm.getLogDenominator()[i]);
        }
        
        for (int i = 0; i < hmm.getPi().size(); i++) {
            prior->add_log_denominator(hmm.getPi()[i]);
        }
        
        prior->set_allocated_log_state_transition_numerator(new hello::RealMatrix(matrixFromMatrix(hmm.getLogANumerator())));
        
        prior->add_end_states(hmm.getNumStates());
        
        for (auto it = hmm.getPi().begin(); it != hmm.getPi().end(); it++) {
            prior->add_pi(*it);
        }
        
        const UIntVec_t minDurations = hmm.getMinStatedDurations();
        
        for (int i = 0; i < minDurations.size(); i++) {
            prior->add_minimum_state_durations(minDurations[i]);
        }
        
        for (auto it = hmm.getForbiddenMotionTransitions().begin(); it != hmm.getForbiddenMotionTransitions().end(); it++) {
            hello::Transition * transition = model.add_forbiddeden_motion_transitions();
            transition->set_from((*it).from);
            transition->set_to((*it).to);
            transition->set_output_id(outputId);
        }
        
        
        
    }
    
    std::ofstream outfile(filename);

    if (outfile.is_open()) {
        model.SerializeToOstream(&outfile);
    }
}


