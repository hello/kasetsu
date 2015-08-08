#ifndef _DATAFILE_H_
#define _DATAFILE_H_

#include <string>
#include "../src/HmmTypes.h"
#include "../src/MultiObsSequence.h"
#include <map>

typedef struct {
    MatrixMap_t rawdata;
    LabelMap_t labels;
} MeasAndLabels_t;

typedef std::vector<MeasAndLabels_t> MeasVec_t;
typedef std::map<std::string,uint32_t> StateSizesMap_t;

class DataFile {
public:
    DataFile();
    ~DataFile();
    
    bool parse(const std::string & filename);
    
    const MeasVec_t & getMeasurements() const;
    uint32_t getNumStates(const std::string & modelName) const;
    
private:

    MeasVec_t _measurements;
    StateSizesMap_t _sizes;
    
};

#endif
