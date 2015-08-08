#ifndef _MULTIOBSSEQUENCE_H_
#define _MULTIOBSSEQUENCE_H_

#include "HmmTypes.h"
#include <vector>

class StateIdxPair {
public:
    StateIdxPair(const uint32_t i1, const uint32_t i2) : from(i1),to(i2) {}
    const uint32_t from;
    const uint32_t to;
};

typedef std::unordered_multimap<uint32_t,StateIdxPair> TransitionMultiMap_t; //key is time index
typedef std::unordered_map<uint32_t, uint32_t> LabelMap_t; //key is time index


class MultiObsSequence {
public:
    MultiObsSequence();
    ~MultiObsSequence();
    
    void addSequence(const MatrixMap_t & rawdata, TransitionMultiMap_t forbiddenTransitions, LabelMap_t labels);
    
    const MatrixMap_t & getMeasurements(const uint32_t sequenceNumber) const;
    
    const TransitionMultiMap_t & getForbiddenTransitions(const uint32_t sequenceNumber) const;
    
    const LabelMap_t & getLabels(const uint32_t sequenceNumber) const;
    
    size_t size() const;
    
private:
    //measurment raw data by measurement sequence
    std::vector<MatrixMap_t> _measurements;

    //restrictions on state transitions by measurement sequence
    std::vector<TransitionMultiMap_t> _forbiddenTransitions;
    
    //labels by measurement sequence
    std::vector<LabelMap_t> _labels;
    
    
};

#endif
