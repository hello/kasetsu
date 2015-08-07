#ifndef _DATAFILE_H_
#define _DATAFILE_H_

#include <string>
#include "../src/HmmTypes.h"
#include "../src/MultiObsSequence.h"
#include <map>

typedef struct {
    HmmDataMatrix_t rawdata;
    LabelMap_t labels;
} MeasAndLabels_t;

typedef std::vector<MeasAndLabels_t> MeasVec_t;
typedef std::multimap<std::string, MeasAndLabels_t> MeasMap_t;
typedef std::map<std::string,uint32_t> StateSizesMap_t;

class DataFile {
public:
    DataFile();
    ~DataFile();
    
    bool parse(const std::string & filename);
    MeasVec_t getMeasurement(const std::string & modelName) const;
    uint32_t getNumStates(const std::string & modelName) const;
private:
    
    
    MeasMap_t _measMap;
    StateSizesMap_t _sizes;
    
};

#endif
