#ifndef _HIDDENMARKOVMODEL_H_
#define _HIDDENMARKOVMODEL_H_

#include "HmmPdfInterface.h"
#include "ReestimationResult.h"
#include <cmath>
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
    ViterbiDecodeResult_t(const ViterbiPath_t & vpath,const HmmFloat_t vcost, const HmmFloat_t bicScore)
    :_path(vpath)
    ,_cost(vcost)
    ,_bic(bicScore)
    {}
    
    ViterbiDecodeResult_t() : _path(ViterbiPath_t()), _cost(-INFINITY),_bic(-INFINITY) {}
   
    ViterbiPath_t getPath() const {
        return _path;
    }
    
    HmmFloat_t getCost() const {
        return _cost;
    }
    
    HmmFloat_t getBIC() const {
        return _bic;
    }
    

private:
        
    ViterbiPath_t _path;
    HmmFloat_t _cost;
    HmmFloat_t _bic;
};


class HiddenMarkovModel;

typedef SHARED_PTR<HiddenMarkovModel> HmmSharedPtr_t;


class HiddenMarkovModel {
public:
    HiddenMarkovModel(const HiddenMarkovModel & copyme);
    HiddenMarkovModel(const HmmDataMatrix_t & A,const UIntVec_t & groupsByStateNumber = UIntVec_t());
    HiddenMarkovModel(const UIntVec_t & groupsByStateNumber);
    
    ~HiddenMarkovModel();
    HiddenMarkovModel & operator = (const HiddenMarkovModel & hmm);

    
    void addModelForState(HmmPdfInterfaceSharedPtr_t);
    
    ReestimationResult_t reestimate(const HmmDataMatrix_t & meas,bool dontReestimateIfScoreDidNotImprove = false);
    ReestimationResult_t reestimateViterbi(const HmmDataMatrix_t & meas);
    HmmFloat_t getModelCost(const HmmDataMatrix_t & meas) const;
    ViterbiDecodeResult_t decode(const HmmDataMatrix_t & meas) const;
    bool reestimateViterbiSplitState(uint32_t s1, uint32_t s2,const ViterbiPath_t & originalViterbi,const HmmDataMatrix_t & meas);
    
    void enlargeWithVSTACS(const HmmDataMatrix_t & meas,uint32_t numToGrow) ;
    void enlargeRandomly(const HmmDataMatrix_t & meas, uint32_t numToGrow) ;
    void  enlargeWithIndirectSplits(const HmmDataMatrix_t & meas, uint32_t numToGrow);
    void getStateInfo(const ViterbiDecodeResult_t & vresult,const HmmDataMatrix_t & logbmap, const uint32_t nstate) const;


    std::string serializeToJson() const;
    HmmSharedPtr_t splitState(uint32_t state) const;
    HmmSharedPtr_t deleteStates(UIntSet_t statesToDelete) const;

    uint32_t getNumberOfFreeParams() const;




private:
    
    
    AlphaBetaResult_t getAlphaAndBeta(int32_t numObs,const HmmDataVec_t & pi, const HmmDataMatrix_t & logbmap, const HmmDataMatrix_t & A) const;
    HmmDataMatrix_t getLogBMap(const ModelVec_t & models,const HmmDataMatrix_t & meas) const;
    
    Hmm3DMatrix_t getLogXi(const AlphaBetaResult_t & alphabeta,const HmmDataMatrix_t & logbmap,size_t numObs) const;
    HmmDataMatrix_t getLogGamma(const AlphaBetaResult_t & alphabeta,size_t numObs) const;
    HmmDataMatrix_t reestimateA(const Hmm3DMatrix_t & xi, const HmmDataMatrix_t & gamma,const size_t numObs) const;
    ModelVec_t reestimateFromGamma(const HmmDataMatrix_t & gamma, const HmmDataMatrix_t & meas) const;
    
    HmmDataMatrix_t getGammaFromViterbiPath(const ViterbiPath_t & path,const size_t numStates, const size_t numObs) const;
    HmmDataMatrix_t reestimateAFromViterbiPath(const ViterbiPath_t & path, const HmmDataMatrix_t & meas,size_t numObs,size_t numStates,const HmmDataMatrix_t & originalA) const;

    ViterbiDecodeResult_t decodePathAndGetCost(int32_t startidx,const ViterbiPathMatrix_t & paths,const HmmDataMatrix_t & phi,const UIntSet_t & restartIndices) const;
    HmmSharedPtr_t splitIndirectly(const ViterbiDecodeResult_t & vresult,const uint32_t nstate) const;

    ModelVec_t _models;
    uint32_t _numStates;
    HmmDataMatrix_t _A;
    HmmDataVec_t _pi;
    
    UIntVec_t _groups;


    
};

#endif //_HIDDENMARKOVMODEL_H_
