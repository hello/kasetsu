
#ifndef _INITIALMODELGENERATOR_H_
#define _INITIALMODELGENERATOR_H_

#include "HmmTypes.h"
#include "HmmPdfInterface.h"
typedef struct {
    HmmDataMatrix_t A;
    ModelVec_t models;
    HmmDataVec_t pi;
} InitialModel_t;

class InitialModelGenerator {
public:
    static InitialModel_t getInitialModelFromData(const HmmDataMatrix_t & meas);
};


#endif //_INITIALMODELGENERATOR_H_