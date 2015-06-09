
#ifndef _INITIALMODELGENERATOR_H_
#define _INITIALMODELGENERATOR_H_

#include "HmmTypes.h"
#include "HmmPdfInterface.h"

typedef enum {
    all,
    motion,
    light,
    sound,
    disturbance
} EInitModel_t;

typedef struct {
    HmmDataMatrix_t A;
    ModelVec_t models;
    HmmDataVec_t pi;
} InitialModel_t;

class InitialModelGenerator {
public:
    static InitialModel_t getInitialModelFromData(const HmmDataMatrix_t & meas,EInitModel_t modelType);
};


#endif //_INITIALMODELGENERATOR_H_