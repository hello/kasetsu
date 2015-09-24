#ifndef _MULTIOBSSEQUENCE_H_
#define _MULTIOBSSEQUENCE_H_

#include "HmmTypes.h"
#include <vector>
#include <assert.h>




class MultiObsSequence {
public:
    MultiObsSequence();
    ~MultiObsSequence();
    
    void addSequence(const MatrixMap_t & rawdata, LabelMap_t labels);
    
    const MatrixMap_t & getMeasurements(const uint32_t sequenceNumber) const;
        
    const LabelMap_t & getLabels(const uint32_t sequenceNumber) const;
    
    MultiObsSequence cloneOne(const uint32_t idx) const;

    
    size_t size() const;
    
private:
    //measurment raw data by measurement sequence
    std::vector<MatrixMap_t> _measurements;
    
    //labels by measurement sequence
    std::vector<LabelMap_t> _labels;
    
    
    
};

#endif
