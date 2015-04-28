
#include "AllModels.h"
#include <gsl/gsl_randist.h>
#include "LogMath.h"
#include <sstream>
#include <random>

#define  MIN_POISSON_MEAN (0.01)
#define  MIN_GAMMA_MEAN (0.01)
#define  MIN_GAMMA_STDDEV (0.1)
#define  MIN_GAMMA_INPUT (0.01)

#define GAMMA_PERTURBATION_MEAN (0.01)
#define GAMMA_PERTURBATION_STDDEV (0.01)
#define POISSON_PERTURBATION_MEAN (0.01)
#define ALPHABET_PERTURBATION  (0.01)

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

GammaModel::GammaModel(const int32_t obsnum,const float mean, const float stddev)
: _mean(mean)
, _stddev(stddev)
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


HmmPdfInterface * GammaModel::clone(bool isPerturbed) const {
    if (isPerturbed) {
    
        return new GammaModel(_obsnum,getPerturbedValue(_mean,GAMMA_PERTURBATION_MEAN,MIN_GAMMA_MEAN),getPerturbedValue(_stddev,GAMMA_PERTURBATION_STDDEV,MIN_GAMMA_STDDEV));

    }
    
    return new GammaModel(_obsnum,_mean,_stddev);
}

HmmPdfInterface * GammaModel::reestimate(const HmmDataVec_t & gammaForThisState, const HmmDataMatrix_t & meas) const {
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
    
    
    return new GammaModel(_obsnum,newmean,newstddev);
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
        
        HmmFloat_t evalValue =gsl_ran_gamma_pdf(val,A,scale);
        
        if (evalValue > 1) {
            int foo = 3;
            foo++;
        }
        ret[i] = eln(evalValue);
    }
    
    return ret;
}

std::string GammaModel::serializeToJson() const {
    char buf[1024];
    memset(buf,0,sizeof(buf));
    snprintf(buf, sizeof(buf), "{\"model_type\" : \"gamma\", \"model_data\": {\"obs_num\": %d, \"stddev\": %f, \"mean\": %f}}",_obsnum,_stddev,_mean);
    
    return std::string(buf);
}

uint32_t GammaModel::getNumberOfFreeParams() const {
    return 2;
}

///////////////////////////////////


PoissonModel::PoissonModel(const int32_t obsnum,const float mu)
:_obsnum(obsnum)
,_mu(mu) {
}

PoissonModel::~PoissonModel() {
    
}

HmmPdfInterface * PoissonModel::clone(bool isPerturbed) const {
    if (isPerturbed) {
        return new PoissonModel(_obsnum,getPerturbedValue(_mu,POISSON_PERTURBATION_MEAN,MIN_POISSON_MEAN));
    }

    return new PoissonModel(_obsnum,_mu);
}

HmmPdfInterface * PoissonModel::reestimate(const HmmDataVec_t & gammaForThisState, const HmmDataMatrix_t & meas) const {
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
    
    return new PoissonModel(_obsnum,newmean);
    
}

HmmDataVec_t PoissonModel::getLogOfPdf(const HmmDataMatrix_t & x) const {
    HmmDataVec_t ret;
    const HmmDataVec_t & vec = x[_obsnum];
    
    ret.resize(vec.size());
    
    for (int32_t i = 0; i < vec.size(); i++) {
        const int32_t meas = (int32_t) vec[i];
        ret[i] = eln(gsl_ran_poisson_pdf(meas, _mu));
    }
    
    return ret;
}

std::string PoissonModel::serializeToJson() const {
    char buf[1024];
    memset(buf,0,sizeof(buf));
    snprintf(buf, sizeof(buf),"{\"model_type\": \"poisson\", \"model_data\": {\"obs_num\": %d, \"mean\": %f}}",_obsnum,_mu);
    return std::string(buf);
}

uint32_t PoissonModel::getNumberOfFreeParams() const {
    return 1;
}

///////////////////////////////////


AlphabetModel::AlphabetModel(const int32_t obsnum,const HmmDataVec_t alphabetprobs,bool allowreestimation)
:_obsnum(obsnum)
,_alphabetprobs(alphabetprobs)
,_allowreestimation(allowreestimation) {
}

AlphabetModel::~AlphabetModel() {
    
}

HmmPdfInterface * AlphabetModel::clone(bool isPerturbed) const {
    
    if (isPerturbed) {
        HmmDataVec_t newalphabet = _alphabetprobs;
        
        for (int i = 0; i < newalphabet.size(); i++) {
            newalphabet[i] = getPerturbedValue(_alphabetprobs[i], ALPHABET_PERTURBATION,1e-6);
        }
        
        return new AlphabetModel(_obsnum,newalphabet,_allowreestimation);

    }
    
    return new AlphabetModel(_obsnum,_alphabetprobs,_allowreestimation);
}

HmmPdfInterface * AlphabetModel::reestimate(const HmmDataVec_t & gammaForThisState, const HmmDataMatrix_t & meas) const {
    
    const HmmDataVec_t & obsvec = meas[_obsnum];

    if  (!_allowreestimation) {
        return new AlphabetModel(_obsnum,_alphabetprobs,_allowreestimation);
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

    return new AlphabetModel(_obsnum,counts,_allowreestimation);

}

HmmDataVec_t AlphabetModel::getLogOfPdf(const HmmDataMatrix_t & x) const {
    HmmDataVec_t ret;
    const HmmDataVec_t & vec = x[_obsnum];
    
    ret.resize(vec.size());
    
    for (int32_t i = 0; i < vec.size(); i++) {
        int32_t idx = (int32_t)vec[i];
        
        ret[i] = eln(_alphabetprobs[idx]);
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
    
    snprintf(buf, sizeof(buf),"{\"model_type\": \"discrete_alphabet\", \"model_data\": {\"obs_num\": %d, \"alphabet_probs\": [%s], \"allow_reestimation\": %s}}",_obsnum,probs.str().c_str(),allowreestiamationstring.c_str());
    return std::string(buf);
}

uint32_t AlphabetModel::getNumberOfFreeParams() const {
    return _alphabetprobs.size();
}
