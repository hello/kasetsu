
#include "AllModels.h"
#include <gsl/gsl_randist.h>
#include "LogMath.h"
#include <sstream>
#include <random>
#include <string.h>

#define  MIN_POISSON_MEAN (0.01)
#define  MIN_GAMMA_MEAN (0.01)
#define  MIN_GAMMA_STDDEV (0.1)
#define  MIN_GAMMA_INPUT (0.01)
#define  MAX_GAMMA_INPUT  (1e5)
#define  MIN_GAUSSIAN_STDDEV(0.1)
#define  MAX_GAUSSIAN_INPUT  (1e5)


#define GAMMA_PERTURBATION_MEAN (0.1)
#define GAMMA_PERTURBATION_STDDEV (0.1)
#define POISSON_PERTURBATION_MEAN (0.1)
#define ALPHABET_PERTURBATION  (0.05)

//between -1 and 1
static HmmFloat_t getRandomFloat() {
    const float r = 2.0 * static_cast <HmmFloat_t> (rand()) / static_cast <HmmFloat_t> (RAND_MAX) - 1.0;
    return r;
}

static HmmFloat_t getPerturbedValue(const HmmFloat_t x, const HmmFloat_t perturbationMaxAmplitude, const HmmFloat_t minVal = -INFINITY) {
    HmmFloat_t y = 0.0;
    int iter = 0;
    
    do {
        y  = x + getRandomFloat() * perturbationMaxAmplitude;
        iter++;
    } while (y < minVal && iter < 10);
    
    return y;
        
    
}

GammaModel::GammaModel(const int32_t obsnum,const float mean, const float stddev, const float weight)
: _mean(mean)
, _stddev(stddev)
, _obsnum(obsnum)
, _weight(weight) {

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


HmmPdfInterfaceSharedPtr_t GammaModel::clone(bool isPerturbed) const {
    if (isPerturbed) {
    
        return HmmPdfInterfaceSharedPtr_t(new GammaModel(_obsnum,getPerturbedValue(_mean,GAMMA_PERTURBATION_MEAN,MIN_GAMMA_MEAN),getPerturbedValue(_stddev,GAMMA_PERTURBATION_STDDEV,MIN_GAMMA_STDDEV),_weight));

    }
    
    return HmmPdfInterfaceSharedPtr_t(new GammaModel(_obsnum,_mean,_stddev,_weight));
}

HmmPdfInterfaceSharedPtr_t GammaModel::reestimate(const HmmDataVec_t & gammaForThisState, const HmmDataMatrix_t & meas, const HmmFloat_t eta) const {
    const HmmDataVec_t & obsvec = meas[_obsnum];
    
    
    HmmFloat_t newmean = 0.0;
    HmmFloat_t oldmean = _mean;
    HmmFloat_t newvariance = 0.0;
    HmmFloat_t dx;
    
    HmmFloat_t numermean = 0.0;
    HmmFloat_t numervariance = 0.0;

    HmmFloat_t denom = 0.0;
    

    for (int32_t t = 0; t < obsvec.size(); t++) {
        dx = obsvec[t] - oldmean;
        numermean += obsvec[t]*gammaForThisState[t];
        numervariance += gammaForThisState[t]*dx*dx;
        denom += gammaForThisState[t];
    }
    
    if (denom > std::numeric_limits<HmmFloat_t>::epsilon()) {
        newmean = numermean / denom;
        newvariance = numervariance / denom;
    }
    else {
        newmean = 0.0;
        newvariance = 0.0;
    }
    
    HmmFloat_t newstddev = sqrt(newvariance);
    
    if (newmean < MIN_GAMMA_MEAN) {
        newmean = MIN_GAMMA_MEAN;
    }
    
    if (newstddev < MIN_GAMMA_STDDEV) {
        newstddev = MIN_GAMMA_STDDEV;
    }
    
    if (std::isnan(newmean) || std::isnan(newstddev)) {
        int foo = 3;
        foo++;
    }
    
    const HmmFloat_t dmean = newmean - _mean;
    const HmmFloat_t dstddev = newstddev - _stddev;
    
    newmean = _mean + eta * dmean;
    newstddev = _stddev + eta * dstddev;
    
    return HmmPdfInterfaceSharedPtr_t(new GammaModel(_obsnum,newmean,newstddev,_weight));
}

HmmDataVec_t GammaModel::getLogOfPdf(const HmmDataMatrix_t & x) const {
    HmmDataVec_t ret;
    const HmmDataVec_t & vec = x[_obsnum];
    
    const HmmFloat_t A = _mean*_mean / (_stddev*_stddev);
    const HmmFloat_t B = _mean/(_stddev*_stddev);
    const HmmFloat_t scale = 1.0 / B;
    
    ret.resize(vec.size());

    for (int32_t i = 0; i < vec.size(); i++) {
        HmmFloat_t val = vec[i];
        
        if (val < MIN_GAMMA_INPUT) {
            val = MIN_GAMMA_INPUT;
        }
        
        if (val > MAX_GAMMA_INPUT) {
            val = MAX_GAMMA_INPUT;
        }
        
        HmmFloat_t evalValue =gsl_ran_gamma_pdf(val,A,scale);
        
        
        ret[i] = _weight * eln(evalValue);
    }
    
    return ret;
}

std::string GammaModel::serializeToJson() const {
    char buf[1024];
    memset(buf,0,sizeof(buf));
    snprintf(buf, sizeof(buf), "{\"model_type\" : \"gamma\", \"model_data\": {\"obs_num\": %d, \"stddev\": %f, \"mean\": %f,\"weight\": %f}}",_obsnum,_stddev,_mean,_weight);
    
    return std::string(buf);
}

uint32_t GammaModel::getNumberOfFreeParams() const {
    return 2;
}

///////////////////////////////////


PoissonModel::PoissonModel(const int32_t obsnum,const float mu,const float weight)
:_obsnum(obsnum)
,_mu(mu)
, _weight(weight) {

}

PoissonModel::~PoissonModel() {

}

HmmPdfInterfaceSharedPtr_t PoissonModel::clone(bool isPerturbed) const {
    if (isPerturbed) {
        return HmmPdfInterfaceSharedPtr_t(new PoissonModel(_obsnum,getPerturbedValue(_mu,POISSON_PERTURBATION_MEAN,MIN_POISSON_MEAN),_weight));
    }

    return HmmPdfInterfaceSharedPtr_t(new PoissonModel(_obsnum,_mu,_weight));
}

HmmPdfInterfaceSharedPtr_t PoissonModel::reestimate(const HmmDataVec_t & gammaForThisState, const HmmDataMatrix_t & meas, const HmmFloat_t eta) const {
    const HmmDataVec_t & obsvec = meas[_obsnum];

    
    HmmFloat_t newmean = 0.0;
    
    HmmFloat_t numer = 0.0;
    HmmFloat_t denom = 0.0;
    
    for (int32_t t = 0; t < obsvec.size(); t++) {
        numer += obsvec[t]*gammaForThisState[t];
        denom += gammaForThisState[t];
    }
    
    if (denom > std::numeric_limits<HmmFloat_t>::epsilon()) {
        newmean = numer / denom;
    }
    else {
        newmean = 0.0;
    }
    
    if (newmean < MIN_POISSON_MEAN) {
        newmean = MIN_POISSON_MEAN;
    }
    
    const HmmFloat_t dmean = newmean - _mu;
    
    newmean = eta * dmean + _mu;
    
    return HmmPdfInterfaceSharedPtr_t(new PoissonModel(_obsnum,newmean,_weight));
    
}

HmmDataVec_t PoissonModel::getLogOfPdf(const HmmDataMatrix_t & x) const {
    HmmDataVec_t ret;
    const HmmDataVec_t & vec = x[_obsnum];
    
    ret.resize(vec.size());
    
    for (int32_t i = 0; i < vec.size(); i++) {
        if (vec[i] < 0) {
            continue;
        }
        
        const uint32_t meas = (uint32_t) vec[i];
        ret[i] = _weight * eln(gsl_ran_poisson_pdf(meas, _mu));
    }
    
    return ret;
}

std::string PoissonModel::serializeToJson() const {
    char buf[1024];
    memset(buf,0,sizeof(buf));
    snprintf(buf, sizeof(buf),"{\"model_type\": \"poisson\", \"model_data\": {\"obs_num\": %d, \"mean\": %f,\"weight\": %f}}",_obsnum,_mu,_weight);
    return std::string(buf);
}

uint32_t PoissonModel::getNumberOfFreeParams() const {
    return 1;
}

///////////////////////////////////


AlphabetModel::AlphabetModel(const int32_t obsnum,const HmmDataVec_t alphabetprobs,bool allowreestimation,const float weight)
:_obsnum(obsnum)
,_alphabetprobs(alphabetprobs)
,_allowreestimation(allowreestimation)
,_weight(weight){
}

AlphabetModel::~AlphabetModel() {
    
}

HmmPdfInterfaceSharedPtr_t AlphabetModel::clone(bool isPerturbed) const {
    
    if (isPerturbed) {
        HmmDataVec_t newalphabet = _alphabetprobs;
        
        for (int i = 0; i < newalphabet.size(); i++) {
            newalphabet[i] = getPerturbedValue(_alphabetprobs[i], ALPHABET_PERTURBATION,1e-6);
        }
        
        return HmmPdfInterfaceSharedPtr_t(new AlphabetModel(_obsnum,newalphabet,_allowreestimation,_weight));

    }
    
    return HmmPdfInterfaceSharedPtr_t(new AlphabetModel(_obsnum,_alphabetprobs,_allowreestimation,_weight));
}

HmmPdfInterfaceSharedPtr_t AlphabetModel::reestimate(const HmmDataVec_t & gammaForThisState, const HmmDataMatrix_t & meas, const HmmFloat_t eta) const {
    
    const HmmDataVec_t & obsvec = meas[_obsnum];

    if  (!_allowreestimation) {
        return HmmPdfInterfaceSharedPtr_t(new AlphabetModel(_obsnum,_alphabetprobs,_allowreestimation,_weight));
    }
    
    HmmDataVec_t counts;
    counts.resize(_alphabetprobs.size());
    
    for (int i = 0; i < _alphabetprobs.size(); i++) {
        counts[i] = 0.0;
    }
    
    HmmFloat_t denom = 0.0;
    
    
    for (int32_t t = 0; t < obsvec.size(); t++) {
        const int32_t idx = (int32_t)obsvec[t];
        counts[idx] += gammaForThisState[t];
        denom += gammaForThisState[t];
    }
    
    if (denom > std::numeric_limits<HmmFloat_t>::epsilon()) {
        for (int i = 0; i < _alphabetprobs.size(); i++) {
            counts[i] /= denom;
        }

    }
    else {
        counts = _alphabetprobs;
    }
    
    HmmDataVec_t dcounts;
    dcounts.resize(_alphabetprobs.size());
    
    for (int i = 0; i < _alphabetprobs.size(); i++) {
        dcounts[i] = counts[i] - _alphabetprobs[i];
    }

    for (int i = 0; i < _alphabetprobs.size(); i++) {
        counts[i] = dcounts[i] * eta + _alphabetprobs[i];
    }
    
    HmmFloat_t sum = 0.0;
    for (int i = 0; i < _alphabetprobs.size(); i++) {
        sum += counts[i];
    }
    
    for (int i = 0; i < _alphabetprobs.size(); i++) {
        counts[i] /= sum;
    }
    
    
    

    return HmmPdfInterfaceSharedPtr_t(new AlphabetModel(_obsnum,counts,_allowreestimation,_weight));

}

HmmDataVec_t AlphabetModel::getLogOfPdf(const HmmDataMatrix_t & x) const {
    HmmDataVec_t ret;
    const HmmDataVec_t & vec = x[_obsnum];
    
    ret.resize(vec.size());
    
    for (int32_t i = 0; i < vec.size(); i++) {
        int32_t idx = (int32_t)vec[i];
        
        ret[i] = _weight * eln(_alphabetprobs[idx]);
    }
    
    return ret;

}

std::string AlphabetModel::serializeToJson() const {
    char buf[1024];
    memset(buf,0,sizeof(buf));
    
    std::stringstream probs;
    bool first = true;
    for (HmmDataVec_t::const_iterator it = _alphabetprobs.begin(); it != _alphabetprobs.end(); it++) {
        if (!first) {
            probs << ",";
        }
        probs << *it;
        first = false;
    }
    
    std::string allowreestiamationstring = "false";
    
    if (_allowreestimation) {
        allowreestiamationstring = "true";
    }
    
    snprintf(buf, sizeof(buf),"{\"model_type\": \"discrete_alphabet\", \"model_data\": {\"obs_num\": %d, \"alphabet_probs\": [%s], \"allow_reestimation\": %s,\"weight\": %f}}",_obsnum,probs.str().c_str(),allowreestiamationstring.c_str(),_weight);
    return std::string(buf);
}

uint32_t AlphabetModel::getNumberOfFreeParams() const {
    return _alphabetprobs.size();
}



///////////////////////////////////





OneDimensionalGaussianModel::OneDimensionalGaussianModel(const int32_t obsnum,const float mean, const float stddev, const float weight)
: _mean(mean)
, _stddev(stddev)
, _obsnum(obsnum)
, _weight(weight) {
    

}


OneDimensionalGaussianModel::~OneDimensionalGaussianModel() {
    
}


HmmPdfInterfaceSharedPtr_t OneDimensionalGaussianModel::clone(bool isPerturbed) const {
    if (isPerturbed) {
        
        return HmmPdfInterfaceSharedPtr_t(new OneDimensionalGaussianModel(_obsnum,getPerturbedValue(_mean,GAMMA_PERTURBATION_MEAN,MIN_GAMMA_MEAN),getPerturbedValue(_stddev,GAMMA_PERTURBATION_STDDEV,MIN_GAMMA_STDDEV),_weight));
        
    }
    
    return HmmPdfInterfaceSharedPtr_t(new OneDimensionalGaussianModel(_obsnum,_mean,_stddev,_weight));
}

HmmPdfInterfaceSharedPtr_t OneDimensionalGaussianModel::reestimate(const HmmDataVec_t & gammaForThisState, const HmmDataMatrix_t & meas, const HmmFloat_t eta) const {
    const HmmDataVec_t & obsvec = meas[_obsnum];
    
    
    HmmFloat_t newmean = 0.0;
    HmmFloat_t oldmean = _mean;
    HmmFloat_t newvariance = 0.0;
    HmmFloat_t dx;
    
    HmmFloat_t numermean = 0.0;
    HmmFloat_t numervariance = 0.0;
    
    HmmFloat_t denom = 0.0;
    
    
    
    for (int32_t t = 0; t < obsvec.size(); t++) {
        dx = obsvec[t] - oldmean;
        numermean += obsvec[t]*gammaForThisState[t];
        numervariance += gammaForThisState[t]*dx*dx;
        denom += gammaForThisState[t];
    }
    
    if (denom > std::numeric_limits<HmmFloat_t>::epsilon()) {
        newmean = numermean / denom;
        newvariance = numervariance / denom;
    }
    else {
        newmean = 0.0;
        newvariance = 0.0;
    }
    
    HmmFloat_t newstddev = sqrt(newvariance);
    
    if (newstddev < MIN_GAMMA_STDDEV) {
        newstddev = MIN_GAMMA_STDDEV;
    }
    
    if (std::isnan(newmean) || std::isnan(newstddev)) {
        int foo = 3;
        foo++;
    }
    
    const HmmFloat_t dmean = newmean - _mean;
    const HmmFloat_t dstddev = newstddev - _stddev;
    
    newmean = _mean + eta * dmean;
    newstddev = _stddev + eta * dstddev;
    
    return HmmPdfInterfaceSharedPtr_t(new OneDimensionalGaussianModel(_obsnum,newmean,newstddev,_weight));
}

HmmDataVec_t OneDimensionalGaussianModel::getLogOfPdf(const HmmDataMatrix_t & x) const {
    HmmDataVec_t ret;
    const HmmDataVec_t & vec = x[_obsnum];
    
    
    ret.resize(vec.size());
    
    for (int32_t i = 0; i < vec.size(); i++) {
        HmmFloat_t val = vec[i];
        
        if (val > MAX_GAUSSIAN_INPUT) {
            val = MAX_GAUSSIAN_INPUT;
        }
        
        HmmFloat_t evalValue = gsl_ran_gaussian_pdf(val - _mean, _stddev);
        
        ret[i] = _weight * eln(evalValue);
    }
    
    return ret;
}

std::string OneDimensionalGaussianModel::serializeToJson() const {
    char buf[1024];
    memset(buf,0,sizeof(buf));
    snprintf(buf, sizeof(buf), "{\"model_type\" : \"gaussian\", \"model_data\": {\"obs_num\": %d, \"stddev\": %f, \"mean\": %f,\"weight\": %f}}",_obsnum,_stddev,_mean,_weight);
    
    return std::string(buf);
}

uint32_t OneDimensionalGaussianModel::getNumberOfFreeParams() const {
    return 2;
}


