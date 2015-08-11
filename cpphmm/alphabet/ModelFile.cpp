#include "ModelFile.h"
#include <rapidjson/document.h>
#include <rapidjson/rapidjson.h>
#include <rapidjson/stringbuffer.h>
#include <rapidjson/writer.h>
#include <fstream>
#include <assert.h>

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
    

    
    assert(d.IsObject());
    assert(d["A"].IsArray());
    assert(d["confusion"].IsArray());
    assert(d["alphabets"].IsObject());
    assert(d["pi"].IsArray());

    
    const HmmDataMatrix_t A = decodeMatrix(d["A"].Begin(),d["A"].End());
    const HmmDataVec_t pi = decodeVector(d["pi"].Begin(),d["pi"].End());

    
    MatrixMap_t alphabets;
    
    for (Value::ConstMemberIterator it = d["alphabets"].MemberBegin();
         it != d["alphabets"].MemberEnd(); it++) {
        
        const HmmDataMatrix_t mtx = decodeMatrix((*it).value.Begin(),(*it).value.End());
        alphabets.insert(std::make_pair((*it).name.GetString(), mtx));
        
    }
    
    return new MultiObsHiddenMarkovModel(alphabets,A);
}

void ModelFile::SaveFile(const MultiObsHiddenMarkovModel & hmm,const std::string & filename) {
    Document d;
    StringBuffer buffer;
    
    Writer<StringBuffer> writer(buffer);
    
    d.SetObject();
    
    const MatrixMap_t alphabets = hmm.getAlphabetMatrix();
    Value alphabetObj;
    alphabetObj.SetObject();
    
    for (MatrixMap_t::const_iterator it = alphabets.begin(); it != alphabets.end(); it++) {
        const std::string & key = (*it).first;
        const HmmDataMatrix_t & mat = (*it).second;
        
        Value name;
        name.SetString(key.c_str(),key.size());
        alphabetObj.AddMember(name,encodeMatrix(d, mat),d.GetAllocator());
    }
    
    d.AddMember("A",encodeMatrix(d,hmm.getAMatrix()),d.GetAllocator());
    d.AddMember("confusion",encodeMatrix(d,hmm.getLastConfusionMatrix()),d.GetAllocator());
    d.AddMember("alphabets",alphabetObj,d.GetAllocator());
    d.AddMember("pi",encodeVector(d,hmm.getPi()),d.GetAllocator());
    d.Accept(writer);
    
    std::ofstream outfile(filename);
    
    outfile << buffer.GetString();
    
    

}


