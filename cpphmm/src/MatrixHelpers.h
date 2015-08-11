#ifndef _MATRIXHELPERS_H_
#define _MATRIXHELPERS_H_

#include "HmmTypes.h"
#include <stdint.h>


void printMat(const std::string & name, const HmmDataMatrix_t & mat,const uint32_t precision = 2);
void printVec(const std::string & name, const HmmDataVec_t & vec);

uint32_t getArgMaxInVec(const HmmDataVec_t & x) ;
ViterbiPathMatrix_t getZeroedPathMatrix(size_t numVecs, size_t vecSize) ;
ViterbiPath_t getZeroedPathVec(size_t vecSize) ;
Hmm3DMatrix_t getLogZeroed3dMatrix(size_t numMats, size_t numVecs, size_t vecSize) ;

Hmm3DMatrix_t getZeroed3dMatrix(size_t numMats, size_t numVecs, size_t vecSize) ;
HmmDataMatrix_t getLogZeroedMatrix(size_t numVecs, size_t vecSize) ;
HmmDataMatrix_t getZeroedMatrix(size_t numVecs, size_t vecSize) ;
HmmDataVec_t getLogZeroedVec(size_t vecSize) ;
HmmDataVec_t getZeroedVec(size_t vecSize) ;
HmmDataMatrix_t getEEXPofMatrix(const HmmDataMatrix_t & x) ;
HmmDataMatrix_t getELNofMatrix(const HmmDataMatrix_t & x);
HmmDataVec_t getUniformVec(size_t vecSize);

#endif
