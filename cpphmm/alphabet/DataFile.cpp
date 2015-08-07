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
    Json::Value sleep;
    Json::Value wake;
    
    LabelMap_t labelMap;
    
    for (int i = 0; i < labels.size(); i++) {
        
        if (hasString(labels[i],"type","SLEEP")) {
            sleep = labels[i];
        }
        
        if (hasString(labels[i],"type","WAKE_UP")) {
            wake = labels[i];
        }
    }
    
    
    if (!sleep.isNull()) {
        const int updated = sleep["updated"].asInt();
        const int original = sleep["original"].asInt();
        
        if (updated > original) {
            //sleep time moved up -- labeling period as awake
            for (int i = original; i <= updated; i++) {
                labelMap.insert(std::make_pair(i, 0));
            }
        }
        else {
            //sleep time moved back -- labeling as sleep
            for (int i = updated; i <= original; i++) {
                labelMap.insert(std::make_pair(i, 1));
            }
        }

    }
    
    
    if (wake.isNull()) {
        const int updated = sleep["updated"].asInt();
        const int original = sleep["original"].asInt();
        
        if (updated > original) {
            //wake time moved up -- labeling period as sleep
            for (int i = original; i <= updated; i++) {
                labelMap.insert(std::make_pair(i, 1));
            }
        }
        else {
            //wake time moved back -- labeling as wake
            for (int i = updated; i <= original; i++) {
                labelMap.insert(std::make_pair(i, 0));
            }
        }

    }
    
     /*

    if (!sleep.isNull() && !wake.isNull()) {
        
        const int updated1 = sleep["updated"].asInt();
        const int updated2 = wake["updated"].asInt();
        
        if (updated2 < updated1) {
            return labelMap;
        }
        
        for (int i = 0; i < updated1; i++) {
            labelMap.insert(std::make_pair(i, 0));
        }
        
        for (int i = updated1; i <= updated2; i++) {
            labelMap.insert(std::make_pair(i, 1));
        }
        
        for (int i = updated2; i < alphabetLength; i++) {
            labelMap.insert(std::make_pair(i, 0));
        }

        
    }
    else if (sleep.isNull()) {
        
    }
    else if (wake.isNull()) {
        
    }
 */
    
    return labelMap;
    
}


static MeasAndLabels_t alphabetToMeasAndLabels(Json::Value alphabet, Json::Value labels) {
    MeasAndLabels_t meas;
    HmmDataMatrix_t raw;
    raw.resize(1);
    
    raw[0] = jsonToVec(alphabet);
    meas.labels = jsonToLabels(labels,raw[0].size());
    meas.rawdata = raw;
    
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
        const Json::Value::Members alphabetNames = alphabets.getMemberNames();
        
        
        for (Json::Value::Members::const_iterator it = alphabetNames.begin(); it != alphabetNames.end(); it++) {
            
            Json::Value alphabet = alphabets[*it];
            _measMap.insert(std::make_pair(*it, alphabetToMeasAndLabels(alphabet,labels)));
            
        }
        
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

MeasVec_t  DataFile::getMeasurement(const std::string & modelName) const {
    MeasVec_t measVec;
    
    if ( _measMap.find(modelName) == _measMap.end()) {
        return measVec;
    }
    
    
    auto mapRange = _measMap.equal_range(modelName);
    
    for (auto it = mapRange.first; it != mapRange.second; it++) {
        measVec.push_back((*it).second);
    }
    
    return measVec;
}








