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
    
    AlphaBetaResult_t(const HmmDataMatrix_t & a, const HmmDataMatrix_t & b,const HmmDataMatrix_t & la, HmmFloat_t c)
    : logalpha(a)
    , logbeta(b)
    , logA(la)
    , logmodelcost(c)
    {}
    
    const HmmDataMatrix_t logalpha;
    const HmmDataMatrix_t logbeta;
    const HmmDataMatrix_t logA;
    const HmmFloat_t logmodelcost;
} ;


class ViterbiDecodeResult_t {
public:
    ViterbiDecodeResult_t(const ViterbiPath_t & vpath,const HmmFloat_t vcost)
    :path(vpath)
    ,cost(vcost)
    {}
    
    const ViterbiPath_t path;
    const HmmFloat_t cost;
};




class HiddenMarkovModel {
public:
    HiddenMarkovModel(const HiddenMarkovModel & copyme);
    HiddenMarkovModel(const HmmDataMatrix_t & A);
    ~HiddenMarkovModel();
    
    void addModelForState(HmmPdfInterface * model);
    
    void InitializeReestimation(const HmmDataMatrix_t & meas);
    
    ReestimationResult_t reestimate(const HmmDataMatrix_t & meas);
    ReestimationResult_t reestimateViterbi(const HmmDataMatrix_t & meas);
    HmmFloat_t getModelCost(const HmmDataMatrix_t & meas) const;
    ViterbiDecodeResult_t decode(const HmmDataMatrix_t & meas) const;
    
    std::string serializeToJson() const;
    HiddenMarkovModel * splitState(uint32_t state) const;




private:
    
    
    AlphaBetaResult_t getAlphaAndBeta(int32_t numObs,const HmmDataVec_t & pi, const HmmDataMatrix_t & logbmap, const HmmDataMatrix_t & A) const;
    HmmDataMatrix_t getLogBMap(const HmmDataMatrix_t & meas) const;
    
    Hmm3DMatrix_t getLogXi(const AlphaBetaResult_t & alphabeta,const HmmDataMatrix_t & logbmap,size_t numObs) const;
    HmmDataMatrix_t getLogGamma(const AlphaBetaResult_t & alphabeta,size_t numObs) const;
    HmmDataMatrix_t reestimateA(const Hmm3DMatrix_t & xi, const HmmDataMatrix_t & gamma,const size_t numObs) const;
    void reestimateFromGamma(const HmmDataMatrix_t & gamma, const HmmDataMatrix_t & meas);
    
    HmmDataMatrix_t getGammaFromViterbiPath(const ViterbiPath_t & path, const HmmDataMatrix_t & meas,size_t numObs) const;
    HmmDataMatrix_t reestimateAFromViterbiPath(const ViterbiPath_t & path, const HmmDataMatrix_t & meas,size_t numObs) const;


    void clearModels();

    ModelVec_t _models;
    uint32_t _numStates;
    HmmDataMatrix_t _A;
    HmmDataVec_t _pi;


    
};

#endif //_HIDDENMARKOVMODEL_H_
