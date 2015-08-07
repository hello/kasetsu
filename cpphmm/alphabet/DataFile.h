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

typedef std::multimap<std::string, MeasAndLabels_t> MeasMap_t;


class DataFile {
public:
    DataFile();
    ~DataFile();
    
    bool parse(const std::string & filename);
    
private:
    
    
    MeasMap_t _measMap;
    
    
};

#endif
