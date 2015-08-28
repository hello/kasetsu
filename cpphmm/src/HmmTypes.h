#ifndef _HMMTYPES_H_
#define _HMMTYPES_H_
#include <stdint.h>
#include <vector>
#include <stdint.h>
#include <iostream>
#include <limits>
#include <algorithm>    
#include "CompatibilityTypes.h"
#include <future>
#include <unordered_map>
#include <map>

typedef double HmmFloat_t;
typedef std::vector<HmmFloat_t> HmmDataVec_t;
typedef std::vector<HmmDataVec_t> HmmDataMatrix_t;
typedef std::vector<HmmDataMatrix_t> Hmm3DMatrix_t;
typedef std::vector<uint32_t> ViterbiPath_t;
typedef std::vector<uint32_t> UIntVec_t;
typedef UNORDERED_SET<uint32_t> UIntSet_t;
typedef UNORDERED_MAP<std::string,HmmDataMatrix_t> MatrixMap_t;
typedef std::map<uint32_t, uint32_t> LabelMap_t; //key is time index

typedef std::vector<ViterbiPath_t> ViterbiPathMatrix_t;

#define  EPSILON (std::numeric_limits<HmmFloat_t>::epsilon())

/* for populating a vector  */
template <class T>
T & operator << (T & ref,typename T::value_type val) {
    ref.push_back(val);
    return ref;
}

template <class T>
T & operator , (T & ref,typename T::value_type val) {
    ref.push_back(val);
    return ref;
}

inline std::ostream & operator << (std::ostream & lhs, const HmmDataVec_t & rhs) {
    bool first = true;
    for (HmmDataVec_t::const_iterator it = rhs.begin() ; it != rhs.end(); it++) {
        if (!first) {
            lhs << ",";
        }
        
        first = false;
        lhs << *it;
    }
    
    return lhs;
}

inline std::ostream & operator << (std::ostream & lhs, const UIntVec_t & rhs) {
    bool first = true;
    for (UIntVec_t::const_iterator it = rhs.begin() ; it != rhs.end(); it++) {
        if (!first) {
            lhs << ",";
        }
        
        first = false;
        lhs << *it;
    }
    
    return lhs;
}

inline std::ostream & operator << (std::ostream & lhs, const UIntSet_t & rhs) {
    bool first = true;
    for (UIntSet_t::const_iterator it = rhs.begin() ; it != rhs.end(); it++) {
        if (!first) {
            lhs << ",";
        }
        
        first = false;
        lhs << *it;
    }
    
    return lhs;
}


typedef std::pair<int32_t,HmmDataVec_t> StateIdxPdfEvalPair_t;
typedef std::pair<int32_t,HmmFloat_t> StateIdxCostPair_t;

typedef std::vector<std::future<StateIdxPdfEvalPair_t> > FuturePdfEvalVec_t;
typedef std::vector<std::future<StateIdxCostPair_t> > FutureCostVec_t;


#endif //_HMMTYPES_H_
