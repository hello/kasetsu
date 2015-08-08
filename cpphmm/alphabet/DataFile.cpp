#include "DataFile.h"
#include <fstream>
#include <json/json.h>

static const char * k_alphabets = "alphabets";
static const char * k_labels = "feedback";
static const char * k_state_sizes = "state_sizes";

static void printKeys(Json::Value json) {
    Json::Value::Members members = json.getMemberNames();
    
    for (auto it = members.begin(); it != members.end(); it++) {
        std::cout << (*it) << std::endl;
    }
}

#define LABEL_PRE_SLEEP (0)
#define LABEL_SLEEP (1)
#define LABEL_POST_SLEEP (2)

static bool hasString(Json::Value json, const std::string & key, const std::string & value) {
    auto members = json.getMemberNames();
    
    bool foundKey = false;
    for (auto it = members.begin(); it != members.end(); it++) {
        if (key == *it) {
            foundKey = true;
            break;
        }
    }
    
    if (!foundKey) {
        return false;
    }
    
    if (!json[key].isString()) {
        return false;
    }
    
    return json[key].asString() == value;
    
}


static HmmDataVec_t jsonToVec(Json::Value value) {
    HmmDataVec_t vec;
    vec.reserve(value.size());
    
    for (int i = 0; i < value.size(); i++) {
        vec.push_back(value[i].asDouble());
    }
    
    return vec;
}

static LabelMap_t jsonToLabels(Json::Value labels, uint32_t alphabetLength) {
    Json::Value sleep = Json::Value(Json::Value::null);
    Json::Value wake = Json::Value(Json::Value::null);
    
    LabelMap_t labelMap;
    
    for (int i = 0; i < labels.size(); i++) {
        
        if (hasString(labels[i],"type","SLEEP")) {
            sleep = labels[i];
        }
        
        if (hasString(labels[i],"type","WAKE_UP")) {
            wake = labels[i];
        }
    }
    
    
    if (sleep.isMember("updated")) {
       
    }
    
    
    if (wake.isMember("updated")) {
        
    }
    
    

    
    if (wake.isMember("updated") && sleep.isMember("updated")) {
        
        const int updated1 = sleep["updated"].asInt();
        const int updated2 = wake["updated"].asInt();
        
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
    else if (sleep.isMember("updated")) {
        const int updated = sleep["updated"].asInt();
        const int original = sleep["original"].asInt();
        
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
    else if (wake.isMember("updated")) {
        const int updated = wake["updated"].asInt();
        const int original = wake["original"].asInt();
        
        if (updated > original) {
            //wake time moved up -- labeling period as sleep
            for (int i = original; i < updated; i++) {
                labelMap.insert(std::make_pair(i, LABEL_SLEEP));
            }
            
            //everything from wake afterwards is "wake"
            for (int i = updated; updated < alphabetLength; i++) {
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


static MeasAndLabels_t alphabetToMeasAndLabels(Json::Value alphabets, Json::Value labels) {
    
    const Json::Value::Members alphabetNames = alphabets.getMemberNames();
    
    MeasAndLabels_t meas;

    for (auto it = alphabetNames.begin(); it != alphabetNames.end(); it++) {
        
        Json::Value alphabet = alphabets[*it];
        
        HmmDataMatrix_t raw;
        raw.resize(1);
        
        raw[0] = jsonToVec(alphabet);
        meas.labels = jsonToLabels(labels,raw[0].size());
        meas.rawdata.insert(std::make_pair(*it,raw));
        
    }
    
   
    
    return meas;
    
}

static void updateStateSizes(StateSizesMap_t & sizes, Json::Value json) {
    Json::Value::Members members = json.getMemberNames();
    
    for (auto it = members.begin(); it != members.end(); it++) {
        if (json[*it].isInt()) {
            sizes.insert(std::make_pair(*it, json[*it].asInt()));
        }
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
    
    Json::Reader reader;
    Json::Value top;
    
    if (!reader.parse(file, top)) {
        return false;
    }
    
    file.close();
    
    if (top.type() != Json::arrayValue) {
        return false;
    }
    
    //loop through each entry
    for (int idx = 0; idx < top.size(); idx++) {
        const Json::Value item = top[idx];
        const Json::Value alphabets = item[k_alphabets];
        const Json::Value labels = item[k_labels];
        const Json::Value stateSizes = item[k_state_sizes];
        
        updateStateSizes(_sizes,stateSizes);
                
        //measurements by model
        
        _measurements.push_back(alphabetToMeasAndLabels(alphabets,labels));

    }
    
    
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









