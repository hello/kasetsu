
#include "AllModels.h"
#include <gsl/gsl_randist.h>


GammaModel::GammaModel(const int32_t obsnum,const float mean, const float stddev)
: _A(mean*mean / (stddev*stddev))
, _B(mean/(stddev*stddev))
, _obsnum(obsnum){

    //A/B = MEAN
    //A/B^2 = variance
    
    // mean / B = variance
    //  mean/variance = B
    //
    //  B * mean = A
    //  mean^2 /variance= A
    
}


GammaModel::~GammaModel() {
    
}

HmmPdfInterface * GammaModel::reestimate(const HmmDataMatrix_t & gamma, const HmmDataMatrix_t & meas) const {
    return NULL;
}

HmmDataVec_t GammaModel::getLogOfPdf(const HmmDataMatrix_t & x) const {
    HmmDataVec_t ret;
    const HmmDataVec_t & vec = x[_obsnum];
    
    ret.resize(vec.size());

    for (int32_t i = 0; i < vec.size(); i++) {
        ret[i] = gsl_ran_gamma_pdf(vec[i],_A,_B);
    }
    
    return ret;
}

///////////////////////////////////


PoissonModel::PoissonModel(const int32_t obsnum,const float mu)
:_obsnum(obsnum)
,_mu(mu) {
}

PoissonModel::~PoissonModel() {
    
}

HmmPdfInterface * PoissonModel::reestimate(const HmmDataMatrix_t & gamma, const HmmDataMatrix_t & meas) const {
    return NULL;
}

HmmDataVec_t PoissonModel::getLogOfPdf(const HmmDataMatrix_t & x) const {
    HmmDataVec_t ret;
    const HmmDataVec_t & vec = x[_obsnum];
    
    ret.resize(vec.size());
    
    for (int32_t i = 0; i < vec.size(); i++) {
        const int32_t meas = (int32_t) vec[i];
        ret[i] = gsl_ran_poisson_pdf(meas, _mu);
    }
    
    return ret;
}



///////////////////////////////////


AlphabetModel::AlphabetModel(const int32_t obsnum,const HmmDataVec_t alphabetprobs)
:_obsnum(obsnum)
,_alphabetprobs(alphabetprobs) {
}

AlphabetModel::~AlphabetModel() {
    
}

HmmPdfInterface * AlphabetModel::reestimate(const HmmDataMatrix_t & gamma, const HmmDataMatrix_t & meas) const {
    return NULL;
}

HmmDataVec_t AlphabetModel::getLogOfPdf(const HmmDataMatrix_t & x) const {
    HmmDataVec_t ret;
    const HmmDataVec_t & vec = x[_obsnum];
    
    ret.resize(vec.size());
    
    for (int32_t i = 0; i < vec.size(); i++) {
        int32_t idx = (int32_t)vec[i];
        
        ret[i] = _alphabetprobs[idx];
    }
    
    return ret;

}
