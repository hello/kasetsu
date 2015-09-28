#ifndef _DATAFILE_H_
#define _DATAFILE_H_

#include <string>
#include "../src/HmmTypes.h"
#include "../src/MultiObsSequence.h"
#include <map>

#define LABEL_PRE_SLEEP (0)
#define LABEL_SLEEP (1)
#define LABEL_POST_SLEEP (2)

#define LABEL_PRE_BED (0)
#define LABEL_IN_BED (1)
#define LABEL_POST_BED (2)

typedef struct {
    MatrixMap_t rawdata;
    LabelMap_t labels;
} MeasAndLabels_t;


typedef std::vector<MeasAndLabels_t> MeasVec_t;
typedef std::map<std::string,uint32_t> StateSizesMap_t;
typedef std::map<std::string,MeasVec_t> MeasMap_t;

class DataFile {
public:
    DataFile();
    ~DataFile();
    
    bool parse(const std::string & filename,bool useAllSequences = false);
    
    MeasVec_t getMeasurements(const std::string & type) const;
    uint32_t getNumStates(const std::string & modelName) const;
    
private:
    
    MeasMap_t _measurements;
    StateSizesMap_t _sizes;
    
};

#endif
