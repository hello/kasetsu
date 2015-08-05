#include "MatrixHelpers.h"
#include "LogMath.h"
#include <iostream>
#include <iomanip>
#include <string.h>


HmmDataMatrix_t getEEXPofMatrix(const HmmDataMatrix_t & x) {
    HmmDataMatrix_t y = x;
    
    for (HmmDataMatrix_t::iterator ivec = y.begin();
         ivec != y.end(); ivec++) {
        HmmDataVec_t & row = *ivec;
        
        for (int i = 0; i < row.size(); i++) {
            row[i] = eexp(row[i]);
        }
    }
    
    return y;
}

HmmDataMatrix_t getELNofMatrix(const HmmDataMatrix_t & x) {
    HmmDataMatrix_t y = x;
    
    for (HmmDataMatrix_t::iterator ivec = y.begin();
         ivec != y.end(); ivec++) {
        HmmDataVec_t & row = *ivec;
        
        for (int i = 0; i < row.size(); i++) {
            row[i] = eln(row[i]);
        }
    }
    
    return y;
}

HmmDataVec_t getZeroedVec(size_t vecSize) {
    HmmDataVec_t vec;
    vec.resize(vecSize);
    memset(vec.data(),0,sizeof(HmmFloat_t) * vecSize);
    return vec;
}

HmmDataVec_t getLogZeroedVec(size_t vecSize) {
    HmmDataVec_t vec;
    vec.resize(vecSize);
    
    for (int i = 0; i < vec.size(); i++) {
        vec[i] = LOGZERO;
    }
    return vec;
}


HmmDataVec_t getUniformVec(size_t vecSize) {
    HmmDataVec_t vec;
    HmmFloat_t a = 1.0 / (HmmFloat_t)vecSize;
    vec.resize(vecSize);
    for (int i = 0; i < vecSize; i++) {
        vec[i] = a;
    }
    return vec;
}

HmmDataMatrix_t getZeroedMatrix(size_t numVecs, size_t vecSize) {
    HmmDataMatrix_t mtx;
    mtx.resize(numVecs);
    
    //allocate and zero out
    for(int j = 0; j < numVecs; j++) {
        mtx[j] = getZeroedVec(vecSize);
    }
    
    return mtx;
}

HmmDataMatrix_t getLogZeroedMatrix(size_t numVecs, size_t vecSize) {
    HmmDataMatrix_t mtx;
    mtx.resize(numVecs);
    
    //allocate and zero out
    for(int j = 0; j < numVecs; j++) {
        mtx[j] = getLogZeroedVec(vecSize);
    }
    
    return mtx;
}


Hmm3DMatrix_t getZeroed3dMatrix(size_t numMats, size_t numVecs, size_t vecSize) {
    Hmm3DMatrix_t mtx3;
    mtx3.reserve(numMats);
    
    for (int i = 0; i < numMats; i++) {
        mtx3.push_back(getZeroedMatrix(numVecs, vecSize));
    }
    
    return mtx3;
}


Hmm3DMatrix_t getLogZeroed3dMatrix(size_t numMats, size_t numVecs, size_t vecSize) {
    (void)getZeroed3dMatrix;
    Hmm3DMatrix_t mtx3;
    mtx3.reserve(numMats);
    
    for (int i = 0; i < numMats; i++) {
        mtx3.push_back(getLogZeroedMatrix(numVecs, vecSize));
    }
    
    return mtx3;
}

ViterbiPath_t getZeroedPathVec(size_t vecSize) {
    ViterbiPath_t path;
    path.resize(vecSize);
    memset(path.data(),0,sizeof(ViterbiPath_t::value_type)*path.size());
    return path;
}


ViterbiPathMatrix_t getZeroedPathMatrix(size_t numVecs, size_t vecSize) {
    ViterbiPathMatrix_t mtx;
    
    for (int i = 0; i < numVecs; i++) {
        mtx.push_back(getZeroedPathVec(vecSize));
    }
    
    return mtx;
}

uint32_t getArgMaxInVec(const HmmDataVec_t & x) {
    HmmFloat_t max = -INFINITY;
    int32_t imax = 0;
    for (int32_t i = 0; i < x.size(); i++) {
        if (x[i] > max) {
            max = x[i];
            imax = i;
        }
    }
    
    //assert(imax >= 0);
    
    return imax;
}

void printMat(const std::string & name, const HmmDataMatrix_t & mat) {
    
    std::cout << std::fixed << std::setprecision(2) << name << std::endl;
    
    for (HmmDataMatrix_t::const_iterator it = mat.begin(); it != mat.end(); it++) {
        bool first = true;
        for (HmmDataVec_t::const_iterator itvec2 = (*it).begin(); itvec2 != (*it).end(); itvec2++) {
            if (!first) {
                std::cout << ",";
            }
            
            std::cout << *itvec2;
            
            
            first = false;
        }
        
        std::cout << std::endl;
    }
    
    
}

void printVec(const std::string & name, const HmmDataVec_t & vec) {
    bool first = true;
    for (HmmDataVec_t::const_iterator itvec2 = vec.begin(); itvec2 != vec.end(); itvec2++) {
        if (!first) {
            std::cout << ",";
        }
        
        std::cout << *itvec2;
        
        
        first = false;
    }
    std::cout << std::endl;
    
}
