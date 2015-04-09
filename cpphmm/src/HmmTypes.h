#ifndef _HMMTYPES_H_
#define _HMMTYPES_H_
#include <stdint.h>
#include <vector>
#include <stdint.h>

typedef float HmmFloat_t;
typedef std::vector<HmmFloat_t> HmmDataVec_t;
typedef std::vector<HmmDataVec_t> HmmDataMatrix_t;
typedef std::vector<HmmDataMatrix_t> Hmm3DMatrix_t;

#endif //_HMMTYPES_H_
