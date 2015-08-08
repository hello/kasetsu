#include "MultiObsSequence.h"

MultiObsSequence::MultiObsSequence() {
    
}

MultiObsSequence::~MultiObsSequence() {
    
}

    
void MultiObsSequence::addSequence(const MatrixMap_t & rawdata, TransitionMultiMap_t forbiddenTransitions, LabelMap_t labels) {
    
    _measurements.push_back(rawdata);
    _forbiddenTransitions.push_back(forbiddenTransitions);
    _labels.push_back(labels);
    
}
    
const MatrixMap_t & MultiObsSequence::getMeasurements(const uint32_t sequenceNumber) const {
    return _measurements[sequenceNumber];
}
    
const TransitionMultiMap_t & MultiObsSequence::getForbiddenTransitions(const uint32_t sequenceNumber) const {
    return _forbiddenTransitions[sequenceNumber];
}
    
const LabelMap_t & MultiObsSequence::getLabels(const uint32_t sequenceNumber) const {
    return _labels[sequenceNumber];
}
    
size_t MultiObsSequence::size() const {
    return _measurements.size();
}
    

    
