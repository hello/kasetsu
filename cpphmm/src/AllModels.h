#ifndef _ALLMODELS_H_
#define _ALLMODELS_H_

#include "HmmPdfInterface.h"


class GammaModel : public HmmPdfInterface {
public:
    GammaModel(const int32_t obsnum,const float mean, const float stddev);
    ~GammaModel();
    
    HmmDataVec_t getLogOfPdf(const HmmDataMatrix_t & x);
private:
    const float _A;
    const float _B;
    const int32_t _obsnum;
};


class PoissonModel : public HmmPdfInterface {
public:
    PoissonModel(const int32_t obsnum,const float mu);
    ~PoissonModel();
    
    HmmDataVec_t getLogOfPdf(const HmmDataMatrix_t & x);
private:
    const int32_t _obsnum;
    const float _mu;
};

class AlphabetModel : public HmmPdfInterface {
public:
    AlphabetModel(const int32_t obsnum,const HmmDataVec_t alphabetprobs);
    ~AlphabetModel();
    
    HmmDataVec_t getLogOfPdf(const HmmDataMatrix_t & x);
    
private:
    const int32_t _obsnum;
    const HmmDataVec_t _alphabetprobs;
};

#endif //_ALLMODELS_H_
