#include "ModelFile.h"
#include <rapidjson/document.h>
#include <rapidjson/rapidjson.h>
#include <rapidjson/stringbuffer.h>
#include <rapidjson/writer.h>
#include <fstream>
#include <assert.h>
#include "online_hmm.pb.h"


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



MultiObsHiddenMarkovModel * ModelFile::LoadFile(const std::string & filename) {
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

void ModelFile::SaveFile(const MultiObsHiddenMarkovModel & hmm,const std::string & filename) {
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


void ModelFile::SaveProtobuf(const MultiObsHiddenMarkovModel &hmm, const std::string &filename,const std::string & outputId) {
    hello::AlphabetHmmPrior prior;
    
    
    prior.set_id("default");
    
    if (outputId == "sleep") {
        prior.set_output_id(hello::OutputId::SLEEP);
    }
    
    if (outputId == "bed") {
        prior.set_output_id(hello::OutputId::BED);
    }

    prior.set_date_created_utc(0);
    prior.set_date_updated_utc(0);
    
    for (auto it = hmm.getLogAlphabetNumerator().begin(); it != hmm.getLogAlphabetNumerator().end(); it++) {
        prior.add_log_observation_model_ids((*it).first);
        *prior.add_log_observation_model_numerator() = matrixFromMatrix((*it).second); //hope this works
    }

    for (int i = 0; i < hmm.getLogDenominator().size(); i++) {
        prior.add_log_denominator(hmm.getLogDenominator()[i]);
    }
    
    for (int i = 0; i < hmm.getPi().size(); i++) {
        prior.add_log_denominator(hmm.getPi()[i]);
    }

    prior.set_allocated_log_state_transition_numerator(new hello::RealMatrix(matrixFromMatrix(hmm.getLogANumerator())));
    
    prior.add_end_states(hmm.getNumStates());
    
    const UIntVec_t minDurations = hmm.getMinStatedDurations();

    for (int i = 0; i < minDurations.size(); i++) {
        prior.add_minimum_state_durations(minDurations[i]);
    }
    
    std::ofstream outfile(filename);

    if (outfile.is_open()) {
        prior.SerializeToOstream(&outfile);
    }
}


