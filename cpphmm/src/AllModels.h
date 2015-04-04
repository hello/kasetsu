#ifndef _ALLMODELS_H_
#define _ALLMODELS_H_

#include "HmmPdfInterface.h"


class GammaModel : public HmmPdfInterface {
public:
    GammaModel();
    ~GammaModel();
    
    HmmFloat_t getLogOfPdf(const HmmDataMatrix_t & x);
};


class PoissonModel : public HmmPdfInterface {
public:
    PoissonModel();
    ~PoissonModel();
    
    HmmFloat_t getLogOfPdf(const HmmDataMatrix_t & x);
};

class AlphabetModel : public HmmPdfInterface {
public:
    AlphabetModel();
    ~AlphabetModel();
    
    HmmFloat_t getLogOfPdf(const HmmDataMatrix_t & x);
};

#endif //_ALLMODELS_H_
