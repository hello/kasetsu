#ifndef _HMMTYPES_H_
#define _HMMTYPES_H_
#include <stdint.h>
#include <vector>
#include <stdint.h>

typedef float HmmFloat_t;
typedef std::vector<HmmFloat_t> HmmDataVec_t;
typedef std::vector<HmmDataVec_t> HmmDataMatrix_t;
typedef std::vector<HmmDataMatrix_t> Hmm3DMatrix_t;

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



#endif //_HMMTYPES_H_
