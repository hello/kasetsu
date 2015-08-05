#include "signalgenerator.h"
#include <gsl/gsl_randist.h>
#include <random>
#include <assert.h>

#include <stdlib.h>     /* srand, rand */
#include <time.h>       /* time */

static HmmFloat_t getRandomFloatBetweenZeroAndOne() {
    return static_cast <HmmFloat_t> (rand()) / static_cast <HmmFloat_t> (RAND_MAX);
}

static uint32_t getRandomAlphabetSymbol(const HmmDataVec_t & probs) {
    const HmmFloat_t f = getRandomFloatBetweenZeroAndOne();
    uint32_t i;
    HmmFloat_t cummprob = 0.0;
    for (i = 0; i < probs.size(); i++) {
        const HmmFloat_t p = probs[i];
        
        if (f >= cummprob && f < cummprob + p) {
            break;
        }
        
        cummprob += p;
    }
    
    return i;
}

static int transitionState(const HmmDataVec_t & row) {
    //number between 0 and 1
    const float f = static_cast <float> (rand()) / static_cast <float> (RAND_MAX);
    
    HmmFloat_t sum = 0.0;
    int i;
    for (i = 0; i < row.size(); i++) {
        sum += row[i];
        
        if (f < sum) {
            return i;
        }
    }
    
    assert(false);
    return 0;
    
}


HmmDataVec_t getGammaSignal(const int length, const HmmDataMatrix_t & A, const HmmDataVec_t & means, const HmmDataVec_t & stddevs ) {
    
    gsl_rng * r;

    gsl_rng_env_setup ();
    r = gsl_rng_alloc (gsl_rng_default);
    
    int istate = 0;
    
    HmmDataVec_t signal;
    
    signal.resize(length);
    
    for (int iter = 0; iter < length; iter++) {
    
        //generate measurement
        const HmmFloat_t mean = means[istate];
        const HmmFloat_t stddev = stddevs[istate];
    
        const HmmFloat_t a = mean * mean / (stddev * stddev);
        const HmmFloat_t b = mean / (stddev * stddev);
        const HmmFloat_t scale = 1.0 / b;
        
        signal[iter] = gsl_ran_gamma(r, a, scale);
        
        
        //determine state to transition to
        istate = transitionState(A[istate]);
    }
    
    gsl_rng_free(r);
    
    return signal;

    
}

HmmDataVec_t getPoissonSignal(const int length, const HmmDataMatrix_t & A, const HmmDataVec_t & means) {
    
    gsl_rng * r;
    
    gsl_rng_env_setup ();
    r = gsl_rng_alloc (gsl_rng_default);
    
    int istate = 0;
    
    HmmDataVec_t signal;
    
    signal.resize(length);
    
    for (int iter = 0; iter < length; iter++) {
        
        //generate measurement
        const HmmFloat_t mean = means[istate];
        
        signal[iter] = gsl_ran_poisson(r, mean);
        
        //determine state to transition to
        istate = transitionState(A[istate]);
    }
    
    gsl_rng_free(r);
    
    return signal;

}

HmmDataVec_t getAlphabetSignal(const int length, const HmmDataMatrix_t & A, const HmmDataMatrix_t & alphabet) {
    
    srand(time(NULL));
    
    
    HmmDataVec_t signal;
    
    signal.resize(length);
    

    int istate = 0;
    
    for (int iter = 0; iter < length; iter++) {
        
        //generate measurement
        const HmmDataVec_t & probs = alphabet[istate];
        
        signal[iter] = (HmmFloat_t)getRandomAlphabetSymbol(probs);
        
        //determine state to transition to
        istate = transitionState(A[istate]);
    }
    
    
    return signal;
}


