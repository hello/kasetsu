#ifndef _HMMHELPERS_H_
#define _HMMHELPERS_H_

#include "HmmPdfInterface.h"
#include "MultiObsSequence.h"
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

class HmmHelpers {
public:
    static AlphaBetaResult_t getAlphaAndBeta(int32_t numObs,const HmmDataVec_t & pi, const HmmDataMatrix_t & logbmap, const HmmDataMatrix_t & A,const uint32_t numStates);
    
    static AlphaBetaResult_t getAlphaAndBeta(int32_t numObs,const HmmDataVec_t & pi, const HmmDataMatrix_t & logbmap, const HmmDataMatrix_t & A,const uint32_t numStates,const LabelMap_t & labels, const TransitionMultiMap_t & forbiddenTransitions);
    
    static Hmm3DMatrix_t getLogXi(const AlphaBetaResult_t & alphabeta,const HmmDataMatrix_t & logbmap,const uint32_t numObs,const uint32_t numStates);
    
    static HmmDataMatrix_t getLogBMap(const ModelVec_t & models, const HmmDataMatrix_t & meas);

};


#endif
