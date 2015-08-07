#include "DataFile.h"
#include <fstream>
#include <json/json.h>

static const char * k_alphabets = "alphabets";
static const char * k_labels = "feedback";


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
    

    if (!sleep.isNull() && !wake.isNull()) {
        const int updated1 = sleep["updated"].asInt();
        const int updated2 = wake["updated"].asInt();
        
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
    
    for (int idx = 0; idx < top.size(); idx++) {
        const Json::Value item = top[idx];
        const Json::Value alphabets = item[k_alphabets];
        const Json::Value labels = item[k_labels];
        
        const Json::Value::Members alphabetNames = alphabets.getMemberNames();
        
        for (Json::Value::Members::const_iterator it = alphabetNames.begin(); it != alphabetNames.end(); it++) {
            
            Json::Value alphabet = alphabets[*it];
            _measMap.insert(std::make_pair(*it, alphabetToMeasAndLabels(alphabet,labels)));
            
        }
        
    }
    
    for (MeasMap_t::const_iterator it = _measMap.begin(); it != _measMap.end(); it++) {
        std::cout << (*it).first << std::endl;
    }
    
    return true;
    
}