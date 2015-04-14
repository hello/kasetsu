#ifndef _HIDDENMARKOVMODEL_H_
#define _HIDDENMARKOVMODEL_H_

#include "HmmPdfInterface.h"
#include "ReestimationResult.h"
/*  
      does forwards backwards calcs, computes gamma, xi, etc.
 
      this class is stateful.
 */

class AlphaBetaResult_t  {
public:
    
    AlphaBetaResult_t(const HmmDataMatrix_t & a, const HmmDataMatrix_t & b,const HmmDataVec_t & normalizingVec,const HmmDataMatrix_t normalizedBMap, HmmFloat_t c)
    : alpha(a)
    , beta(b)
    , normalizing(normalizingVec)
    , bmap(normalizedBMap)
    , logmodelcost(c)
    {}
    
    const HmmDataMatrix_t alpha;
    const HmmDataMatrix_t beta;
    const HmmDataVec_t    normalizing;
    const HmmDataMatrix_t bmap;
    const HmmFloat_t logmodelcost;
} ;




class HiddenMarkovModel {
public:
    HiddenMarkovModel(const HmmDataMatrix_t & A);
    ~HiddenMarkovModel();
    
    void addModelForState(HmmPdfInterface * model);
    
    ReestimationResult_t reestimate(const HmmDataMatrix_t & meas);


private:
    
    ModelVec_t _models;
    
    AlphaBetaResult_t getAlphaAndBeta(int32_t numObs,const HmmDataVec_t & pi, const HmmDataMatrix_t & logbmap, const HmmDataMatrix_t A) const;
    HmmDataMatrix_t getLogBMap(const HmmDataMatrix_t & meas) const;
    
    Hmm3DMatrix_t getXi(const AlphaBetaResult_t & alphabeta,size_t numObs) const;
    HmmDataMatrix_t getGamma(const Hmm3DMatrix_t & xi,size_t numObs) const;
    HmmDataMatrix_t reestimateA(const Hmm3DMatrix_t & xi, const HmmDataMatrix_t & gamma,const size_t numObs) const;

    void clearModels();

    int32_t _numStates;
    HmmDataMatrix_t _A;
    HmmDataVec_t _pi;


    
};

#endif //_HIDDENMARKOVMODEL_H_
