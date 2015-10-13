#include "DataFile.h"
#include <fstream>
#include <rapidjson/document.h>
#include "CommonTypes.h"

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






static LabelMap_t jsonToLabelsForSleep(Value::ConstValueIterator begin,Value::ConstValueIterator end, uint32_t alphabetLength) {
    
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
            labelMap.insert(std::make_pair(i, LABEL_PRE_SLEEP));
        }
        
        for (int i = updated1; i <= updated2; i++) {
            labelMap.insert(std::make_pair(i, LABEL_SLEEP));
        }
        
        for (int i = updated2; i < alphabetLength; i++) {
            labelMap.insert(std::make_pair(i, LABEL_POST_SLEEP));
        }

        
    }
    else {
        
        if (hasSleep) {
            const int updated = (*sleep)["updated"].GetInt();
            
            for (int i = 0; i < updated; i++) {
                labelMap.insert(std::make_pair(i, LABEL_PRE_SLEEP));
            }
            
            for (int i = updated + SLEEP_SPACING; i < updated + SLEEP_LABEL_PERIOD; i++) {
                labelMap.insert(std::make_pair(i, LABEL_SLEEP));
            }
            
        }
        
        if (hasWake) {
            const int updated = (*wake)["updated"].GetInt();
            
            //wake time moved up -- labeling period as sleep
            for (int i = updated - SLEEP_LABEL_PERIOD; i < updated; i++) {
                labelMap.insert(std::make_pair(i, LABEL_SLEEP));
            }
            
            //everything from wake afterwards is "wake"
            for (int i = updated; i < alphabetLength; i++) {
                labelMap.insert(std::make_pair(i, LABEL_POST_SLEEP));
                
            }
            
        }
    }
    
    
    if (hasInBed) {
        const int updated = (*inbed)["updated"].GetInt();
        for (int i = 0; i < updated; i++) {
            labelMap.insert(std::make_pair(i, LABEL_PRE_SLEEP));
        }
    }
    
    if (hasOutOfBed) {
        const int updated = (*outofbed)["updated"].GetInt();
        for (int i = updated; i < alphabetLength; i++) {
            labelMap.insert(std::make_pair(i, LABEL_POST_SLEEP));
        }
    }
 
     
    
    return labelMap;
    
}

static LabelMap_t jsonToLabelsForBed(Value::ConstValueIterator begin,Value::ConstValueIterator end, uint32_t alphabetLength) {
    

    Value::ConstValueIterator inbed;
    Value::ConstValueIterator outofbed;
    
    LabelMap_t labelMap;
    bool hasInBed = false;
    bool hasOutOfBed = false;
    
    for (auto it = begin; it != end; it++) {
        
        if (hasString(it->MemberBegin(),it->MemberEnd(),"type","IN_BED")) {
            inbed = it;
            hasInBed = true;
        }
        
        if (hasString(it->MemberBegin(),it->MemberEnd(),"type","OUT_OF_BED")) {
            outofbed = it;
            hasOutOfBed = true;
        }
    }
    
    
    if (hasInBed && hasOutOfBed) {
        
        const int updated1 = (*inbed)["updated"].GetInt();
        const int updated2 = (*outofbed)["updated"].GetInt();
        
        if (updated2 < updated1) {
            return labelMap;
        }
        
        for (int i = 0; i < updated1; i++) {
            labelMap.insert(std::make_pair(i, LABEL_PRE_BED));
        }
        
        for (int i = updated1; i <= updated2; i++) {
            labelMap.insert(std::make_pair(i, LABEL_IN_BED));
        }
        
        for (int i = updated2; i < alphabetLength; i++) {
            labelMap.insert(std::make_pair(i, LABEL_POST_BED));
        }
        
        
    }
    else {
        
        if (hasInBed) {
            const int updated = (*inbed)["updated"].GetInt();
            
            for (int i = 0; i < updated; i++) {
                labelMap.insert(std::make_pair(i, LABEL_PRE_BED));
            }
            
            for (int i = updated + SLEEP_SPACING; i < updated + SLEEP_LABEL_PERIOD; i++) {
                labelMap.insert(std::make_pair(i, LABEL_IN_BED));
            }
            
        }
        
        if (hasOutOfBed) {
            const int updated = (*outofbed)["updated"].GetInt();
            
            //wake time moved up -- labeling period as sleep
            for (int i = updated - SLEEP_LABEL_PERIOD; i < updated; i++) {
                labelMap.insert(std::make_pair(i, LABEL_IN_BED));
            }
            
            //everything from wake afterwards is "wake"
            for (int i = updated; i < alphabetLength; i++) {
                labelMap.insert(std::make_pair(i, LABEL_POST_BED));
                
            }
            
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

static MeasAndLabels_t alphabetToMeasAndLabels(Value::ConstMemberIterator alphabetBegin,Value::ConstMemberIterator alphabetEnd,Value::ConstValueIterator labelsBegin, Value::ConstValueIterator labelsEnd,bool isForSleep) {
    
    MeasAndLabels_t meas;
    uint32_t size = 0;
    for (Value::ConstMemberIterator it = alphabetBegin; it != alphabetEnd; it++) {
        
        const std::string key = it->name.GetString();
        
        /*
        if (key == "disturbances") {
            continue;
        }
         */
         
         
        
        HmmDataMatrix_t raw;
        raw.resize(1);
        raw[0] = jsonToVec(it->value.Begin(), it->value.End() );
        
        meas.rawdata.insert( std::make_pair(key,raw));
        size = raw[0].size();
        
        if (key == "motion") {
            for (int t = 0; t < raw[0].size(); t++) {
                if (raw[0][t] == 6.0) {
                    raw[0][t] = 0.0;
                }
            }
        }
    }
    
    if (isForSleep) {
        meas.labels = jsonToLabelsForSleep(labelsBegin,labelsEnd,size);
    }
    else {
        meas.labels = jsonToLabelsForBed(labelsBegin,labelsEnd,size);
    }
    
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

bool DataFile::parse(const std::string & filename,bool useAllSequences) {
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
    MeasVec_t sleepMeas;
    MeasVec_t bedMeas;
    
    for (Value::ConstValueIterator itr = document.Begin(); itr != document.End(); ++itr) {
        assert(itr->IsObject());
        
        MeasAndLabels_t meas1 = alphabetToMeasAndLabels((*itr)[k_alphabets].MemberBegin(),(*itr)[k_alphabets].MemberEnd(),(*itr)[k_labels].Begin(),(*itr)[k_labels].End(),true);
        
        if (!meas1.labels.empty() || useAllSequences) {
            sleepMeas.push_back(meas1);
        }
        
        MeasAndLabels_t meas2 = alphabetToMeasAndLabels((*itr)[k_alphabets].MemberBegin(),(*itr)[k_alphabets].MemberEnd(),(*itr)[k_labels].Begin(),(*itr)[k_labels].End(),false);
        
        if (!meas2.labels.empty() || useAllSequences) {
            bedMeas.push_back(meas2);
        }
        
        updateStateSizes(_sizes,(*itr)[k_state_sizes].MemberBegin(),(*itr)[k_state_sizes].MemberEnd());
        
        count++;
    }
    
    _measurements[SLEEP_ENUM_STRING] = sleepMeas;
    _measurements[BED_ENUM_STRING] = bedMeas;


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

MeasVec_t DataFile::getMeasurements(const std::string & type) const {
    MeasVec_t measvec;
    
    auto it = _measurements.find(type);

    if (it == _measurements.end()) {
        return measvec;
    }
    
    return (*it).second;
        
}









