#ifndef _ALLMODELS_H_
#define _ALLMODELS_H_

#include "HmmPdfInterface.h"


class GammaModel : public HmmPdfInterface {
public:
    GammaModel(const int32_t obsnum,const float mean, const float stddev);
    ~GammaModel();
    
    HmmPdfInterface * reestimate(const HmmDataVec_t & gammaForThisState, const HmmDataMatrix_t & meas) const;
    HmmDataVec_t getLogOfPdf(const HmmDataMatrix_t & x) const;
private:
    const float _A;
    const float _B;
    const int32_t _obsnum;
};

///////////////////////////////////

class PoissonModel : public HmmPdfInterface {
public:
    PoissonModel(const int32_t obsnum,const float mu);
    ~PoissonModel();
    
    HmmPdfInterface * reestimate(const HmmDataVec_t & gammaForThisState, const HmmDataMatrix_t & meas) const;
    HmmDataVec_t getLogOfPdf(const HmmDataMatrix_t & x) const;
private:
    const int32_t _obsnum;
    const float _mu;
};

////////////////////////////////////

class AlphabetModel : public HmmPdfInterface {
public:
    AlphabetModel(const int32_t obsnum,const HmmDataVec_t alphabetprobs,bool allowreestimation);
    ~AlphabetModel();
    
    HmmPdfInterface * reestimate(const HmmDataVec_t  & gammaForThisState, const HmmDataMatrix_t & meas) const;
    HmmDataVec_t getLogOfPdf(const HmmDataMatrix_t & x) const ;
    
private:
    const int32_t _obsnum;
    const HmmDataVec_t _alphabetprobs;
    const bool _allowreestimation;
};

#endif //_ALLMODELS_H_
