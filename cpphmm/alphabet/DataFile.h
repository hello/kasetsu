#ifndef _DATAFILE_H_
#define _DATAFILE_H_

#include <string>
#include "../src/HmmTypes.h"
#include "../src/MultiObsSequence.h"
#include <map>

#define LABEL_PRE_SLEEP (0)

#define LABEL_PRE_IN_BED (1)
#define LABEL_SLEEP (2)
#define LABEL_POST_IN_BED (3)

#define LABEL_POST_SLEEP (4)

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
