#include "MultiObsSequence.h"

MultiObsSequence::MultiObsSequence() {
    
}

MultiObsSequence::~MultiObsSequence() {
}



    
void MultiObsSequence::addSequence(const MatrixMap_t & rawdata, LabelMap_t labels) {
    
    _measurements.push_back(rawdata);
    _labels.push_back(labels);
    
}

MultiObsSequence MultiObsSequence::cloneOne(const uint32_t idx) const {
    MultiObsSequence newSequence;
    
    newSequence.addSequence(_measurements[idx], _labels[idx]);
    
    return newSequence;
}
    
const MatrixMap_t & MultiObsSequence::getMeasurements(const uint32_t sequenceNumber) const {
    return _measurements[sequenceNumber];
}
    

const LabelMap_t & MultiObsSequence::getLabels(const uint32_t sequenceNumber) const {
    return _labels[sequenceNumber];
}
    
size_t MultiObsSequence::size() const {
    return _measurements.size();
}





    
