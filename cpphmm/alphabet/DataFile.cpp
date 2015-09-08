#include "DataFile.h"
#include <fstream>
#include <rapidjson/document.h>

static const char * k_alphabets = "alphabets";
static const char * k_labels = "feedback";
static const char * k_state_sizes = "state_sizes";

#define SLEEP_LABEL_PERIOD (36)
#define SLEEP_SPACING (0)

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
    Value::ConstValueIterator inbed;
    Value::ConstValueIterator outofbed;

    LabelMap_t labelMap;
    
    bool hasWake = false;
    bool hasSleep = false;
    bool hasInBed = false;
    bool hasOutOfBed = false;
    
    for (auto it = begin; it != end; it++) {
        
        if (hasString(it->MemberBegin(),it->MemberEnd(),"type","SLEEP")) {
            sleep = it;
            hasSleep = true;
        }
        
        if (hasString(it->MemberBegin(),it->MemberEnd(),"type","WAKE_UP")) {
            wake = it;
            hasWake = true;
        }
        
        if (hasString(it->MemberBegin(),it->MemberEnd(),"type","IN_BED")) {
            inbed = it;
            hasInBed = true;
        }
        
        if (hasString(it->MemberBegin(),it->MemberEnd(),"type","OUT_OF_BED")) {
            outofbed = it;
            hasOutOfBed = true;
        }
    }
    
    
    
    
    if (hasWake && hasSleep) {
        
        const int updated1 = (*sleep)["updated"].GetInt();
        const int updated2 = (*wake)["updated"].GetInt();
        
        if (updated2 < updated1) {
            return labelMap;
        }
        
        for (int i = 0; i < updated1; i++) {
            labelMap[i] = LABEL_PRE_SLEEP;

        }
        
        for (int i = updated1; i < updated2; i++) {
            labelMap[i] = LABEL_SLEEP;

        }
        
        for (int i = updated2; i < alphabetLength; i++) {
            labelMap[i] = LABEL_POST_SLEEP;
        }
        
        labelMap[updated1 - 1] = LABEL_PRE_IN_BED;
        labelMap[updated2 - 1] = LABEL_POST_IN_BED;

    }
    else {
    
        if (hasSleep) {
            const int updated = (*sleep)["updated"].GetInt();
            
            for (int i = 0; i < updated; i++) {
                labelMap[i] = LABEL_PRE_SLEEP;
            }
            
            
            for (int i = updated + SLEEP_SPACING; i < updated + SLEEP_LABEL_PERIOD; i++) {
                labelMap[i] = LABEL_SLEEP;
            }
            
            labelMap[updated - 1] = LABEL_PRE_IN_BED;

            
        }
        
        if (hasWake) {
            const int updated = (*wake)["updated"].GetInt();
            
            //wake time moved up -- labeling period as sleep
            for (int i = updated - SLEEP_LABEL_PERIOD; i < updated; i++) {
                labelMap[i] = LABEL_SLEEP;
            }
            
            
            //everything from wake afterwards is "wake"
            for (int i = updated; i < alphabetLength; i++) {
                labelMap[i] = LABEL_POST_SLEEP;
            }
            
            labelMap[updated - 1] = LABEL_POST_IN_BED;
        }
    }
    
    
    if (hasInBed && hasSleep) {
        const int updatedInBed = (*inbed)["updated"].GetInt();
        const int updatedSleep = (*sleep)["updated"].GetInt();
        
        for (int i = updatedInBed; i < updatedSleep; i++) {
            labelMap[i] = LABEL_PRE_IN_BED;
        }
    }
    
    if (hasOutOfBed && hasWake) {
        const int updatedOutOfBed = (*outofbed)["updated"].GetInt();
        const int updatedWake = (*wake)["updated"].GetInt();

        for (int i = updatedWake; i < updatedOutOfBed; i++) {
            labelMap[i] = LABEL_POST_IN_BED;
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









