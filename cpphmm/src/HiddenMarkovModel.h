#ifndef _HIDDENMARKOVMODEL_H_
#define _HIDDENMARKOVMODEL_H_

#include "HmmPdfInterface.h"
/*  
      does forwards backwards calcs, computes gamma, xi, etc.
 
      this class is stateful.
 */

class AlphaBetaResult_t  {
public:
    
    AlphaBetaResult_t(const HmmDataMatrix_t & a, const HmmDataMatrix_t & b, HmmFloat_t c)
    : alpha(a)
    , beta(b)
    , logmodelcost(c)
    {}
    
    const HmmDataMatrix_t alpha;
    const HmmDataMatrix_t beta;
    const HmmFloat_t logmodelcost;
} ;



class HiddenMarkovModel {
public:
    HiddenMarkovModel(int32_t numStates);
    ~HiddenMarkovModel();
    
    void addModelForState(int32_t stateNum, HmmPdfInterface * model);
    
private:
    
    
    AlphaBetaResult_t getAlphaAndBeta(int32_t numObs,const HmmDataVec_t & pi, const HmmDataMatrix_t & logbmap, const HmmDataMatrix_t A) const;
    void reestimate();
    
    int32_t _numStates;
    
};

#endif //_HIDDENMARKOVMODEL_H_
