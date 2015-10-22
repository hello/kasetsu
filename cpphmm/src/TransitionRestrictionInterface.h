#ifndef _TRANSITIONRESTRICTIONINTERFACE_H_
#define _TRANSITIONRESTRICTIONINTERFACE_H_
#include "HmmTypes.h"
#include <assert.h>

class StateIdxPair {
public:
    StateIdxPair(const uint32_t i1, const uint32_t i2) : from(i1),to(i2) {}
    uint32_t from;
    uint32_t to;
    
    bool operator == (const StateIdxPair & t) const {
        return from == t.from && to == t.to;
    }
    
    StateIdxPair & operator = (const StateIdxPair & t) {
        from = t.from;
        to = t.to;
        
        return *this;
    }
};

struct StateIdxPairHash {
    std::size_t operator()(const StateIdxPair & k) const{
        using std::size_t;
        
        // Compute individual hash values for first,
        // second and third and combine them using XOR
        // and bit shifting:
        assert(sizeof(size_t) >= 8);
        const size_t hashval = (size_t) k.from + (((size_t)k.to) << 32);
        return hashval;
    }
};


typedef std::map<uint32_t,StateIdxPair> TransitionMap_t; //key is time index
typedef UNORDERED_MAP<StateIdxPair,int32_t,StateIdxPairHash> TransitionAtTime_t; //key is time index
typedef UNORDERED_MAP<StateIdxPair,int32_t,StateIdxPairHash> TransitionAtTime_t; //key is time index

typedef std::vector<TransitionAtTime_t> TransitionAtTimeVec_t;
typedef std::vector<StateIdxPair> TransitionVector_t;
typedef UNORDERED_MULTIMAP<uint32_t,StateIdxPair> TransitionMultiMap_t; //key is time index


class TransitionRestrictionInterface {
public:
    virtual ~TransitionRestrictionInterface() {}
    
    virtual TransitionMultiMap_t getTimeIndexedRestrictions(const MatrixMap_t & measurements) const = 0;

};

typedef SHARED_PTR<TransitionRestrictionInterface> TransitionRestrictionSharedPtr_t;
typedef std::vector<TransitionRestrictionSharedPtr_t> TransitionRestrictionVector_t;


#endif //_TRANSITIONRESTRICTIONINTERFACE_H_
