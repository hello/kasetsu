#include "DataFile.h"
#include <fstream>
#include <rapidjson/document.h>

static const char * k_alphabets = "alphabets";
static const char * k_labels = "feedback";
static const char * k_state_sizes = "state_sizes";

using namespace rapidjson;


static bool hasString(Value::ConstMemberIterator begin,Value::ConstMemberIterator end, const std::string & key, const std::string & value) {
    
    bool foundKey = false;

    Value::ConstMemberIterator it;
    
    for (it = begin; it != end; it++) {
        if (key == it->name.GetString()) {
            foundKey = true;
            break;
        }
    }
    
    if (!foundKey) {
        return false;
    }
    
    return it->value.GetString() == value;
    
}






static LabelMap_t jsonToLabels(Value::ConstValueIterator begin,Value::ConstValueIterator end, uint32_t alphabetLength) {
    
    Value::ConstValueIterator sleep;
    Value::ConstValueIterator wake;
    LabelMap_t labelMap;
    
    bool hasWake = false;
    bool hasSleep = false;
    
    
    for (auto it = begin; it != end; it++) {
        
        if (hasString(it->MemberBegin(),it->MemberEnd(),"type","SLEEP")) {
            sleep = it;
            hasSleep = true;
        }
        
        if (hasString(it->MemberBegin(),it->MemberEnd(),"type","WAKE_UP")) {
            wake = it;
            hasWake = true;
        }
    }
    
    
    
    
    if (hasWake && hasSleep) {
        
        const int updated1 = (*sleep)["updated"].GetInt();
        const int updated2 = (*wake)["updated"].GetInt();
        
        if (updated2 < updated1) {
            return labelMap;
        }
        
        for (int i = 0; i < updated1; i++) {
            labelMap.insert(std::make_pair(i, LABEL_PRE_SLEEP));
        }
        
        for (int i = updated1; i <= updated2; i++) {
            labelMap.insert(std::make_pair(i, LABEL_SLEEP));
        }
        
        for (int i = updated2; i < alphabetLength; i++) {
            labelMap.insert(std::make_pair(i, LABEL_POST_SLEEP));
        }

        
    }
    
    else if (hasSleep) {
        const int updated = (*sleep)["updated"].GetInt();
        const int original = (*sleep)["original"].GetInt();
        
        if (updated > original) {
            //sleep time moved up -- labeling period as awake
            for (int i = 0; i < updated; i++) {
                labelMap.insert(std::make_pair(i, LABEL_PRE_SLEEP));
            }
            
            labelMap.insert(std::make_pair(updated, LABEL_SLEEP)); //begin sleep
            
        }
        else {
            //labeling everything up to sleep as wake
            for (int i = 0; i < updated; i++) {
                labelMap.insert(std::make_pair(i, LABEL_PRE_SLEEP));
            }
            
            //sleep time moved back -- labeling as sleep
            for (int i = updated; i <= original; i++) {
                labelMap.insert(std::make_pair(i, LABEL_SLEEP));
            }
        }

    }
    else if (hasWake) {
        const int updated = (*wake)["updated"].GetInt();
        const int original = (*wake)["original"].GetInt();
        
        if (updated > original) {
            //wake time moved up -- labeling period as sleep
            for (int i = original; i < updated; i++) {
                labelMap.insert(std::make_pair(i, LABEL_SLEEP));
            }
            
            //everything from wake afterwards is "wake"
            for (int i = updated; i < alphabetLength; i++) {
                labelMap.insert(std::make_pair(i, LABEL_POST_SLEEP));
                
            }
        }
        else {
            //wake time moved back -- labeling as wake
            for (int i = updated; i < alphabetLength; i++) {
                labelMap.insert(std::make_pair(i, LABEL_POST_SLEEP));
            }
            
            labelMap.insert(std::make_pair(updated - 1, LABEL_SLEEP));
            
        }

    }
 
     
    
    return labelMap;
    
}


static HmmDataVec_t jsonToVec(Value::ConstValueIterator begin, Value::ConstValueIterator end) {
    HmmDataVec_t vec;
    vec.reserve(1024);
    
    for (Value::ConstValueIterator it = begin; it != end; it++) {
        vec.push_back(it->GetDouble());
    }
    
    return vec;
}

MeasAndLabels_t alphabetToMeasAndLabels(Value::ConstMemberIterator alphabetBegin,Value::ConstMemberIterator alphabetEnd,Value::ConstValueIterator labelsBegin, Value::ConstValueIterator labelsEnd) {
    
    MeasAndLabels_t meas;
    uint32_t size = 0;
    for (Value::ConstMemberIterator it = alphabetBegin; it != alphabetEnd; it++) {
        
        const std::string key = it->name.GetString();
        
        
        if (key == "disturbances") {
            continue;
        }
         
        
        HmmDataMatrix_t raw;
        raw.resize(1);
        raw[0] = jsonToVec(it->value.Begin(), it->value.End() );
        
        meas.rawdata.insert( std::make_pair(key,raw));
        size = raw[0].size();
    }
    
    meas.labels = jsonToLabels(labelsBegin,labelsEnd,size);
    
    return meas;
}





static void updateStateSizes(StateSizesMap_t & sizes, Value::ConstMemberIterator begin, Value::ConstMemberIterator end) {
    
    for (auto it = begin; it != end; it++) {
        const std::string key = it->name.GetString();
        const uint32_t value = it->value.GetInt();
        sizes.insert(std::make_pair(key,value));
    }
}
 


DataFile::DataFile() {
}

DataFile::~DataFile() {
    
}

bool DataFile::parse(const std::string & filename) {
    std::ifstream file(filename);
    
    if (!file.is_open()) {
        return false;
    }
    
    file.seekg(0,std::ios::end);
    std::string str;
    str.reserve(file.tellg());
    file.seekg(0, std::ios::beg);
    
    str.assign((std::istreambuf_iterator<char>(file)),
               std::istreambuf_iterator<char>());
    
    Document document;
    
    document.Parse(str.c_str());
    
    assert(document.IsArray());
    
    uint32_t count = 0;
    
    //loop through each entry
    for (Value::ConstValueIterator itr = document.Begin(); itr != document.End(); ++itr) {
        assert(itr->IsObject());
        
        _measurements.push_back(alphabetToMeasAndLabels((*itr)[k_alphabets].MemberBegin(),(*itr)[k_alphabets].MemberEnd(),(*itr)[k_labels].Begin(),(*itr)[k_labels].End()));
        
        
      
        
        updateStateSizes(_sizes,(*itr)[k_state_sizes].MemberBegin(),(*itr)[k_state_sizes].MemberEnd());
        
        count++;
    }

    std::cout << "processed " << count << " items" << std::endl;

    
    
    return true;
    
}

uint32_t DataFile::getNumStates(const std::string & modelName) const {
    auto it = _sizes.find(modelName);
    
    if (it == _sizes.end()) {
        return 0;
    }
    
    return (*it).second;
}

const MeasVec_t & DataFile::getMeasurements() const {
    return _measurements;
}









