#include "HmmHelpers.h"
#include "LogMath.h"
#include "MatrixHelpers.h"
#include <assert.h>

#define FORBIDDEN_TRANSITION_PENALTY LOGZERO
#define NON_LABEL_PENALTY LOGZERO

template <typename T>
std::vector<size_t> sort_indexes(const std::vector<T> &v) {
    
    // initialize original index locations
    std::vector<size_t> idx(v.size());
    for (size_t i = 0; i != idx.size(); ++i) idx[i] = i;
    
    // sort indexes based on comparing values in v
    sort(idx.begin(), idx.end(),
         [&v](size_t i1, size_t i2) {return v[i1] < v[i2];});
    
    return idx;
}


static HmmDataMatrix_t getLogAWithForbiddenStates(const HmmDataMatrix_t & logA,const TransitionMultiMap_t & forbiddenTransitions, uint32_t t) {
    
    HmmDataMatrix_t logA2 = logA;
    
    auto itpair =  forbiddenTransitions.equal_range(t);
    
    for (auto it = itpair.first; it != itpair.second; it++) {
        const uint32_t i1 = (*it).second.from;
        const uint32_t i2 = (*it).second.to;
        
        logA2[i1][i2] = FORBIDDEN_TRANSITION_PENALTY;
    }
    
    return logA2;
    
}

static bool getLabel(uint32_t & label, const uint32_t t, const LabelMap_t & labels) {
    auto it = labels.find(t);
    
    if (it == labels.end()) {
        return false;
    }
    
    label = (*it).second;
    
    return true;
}

AlphaBetaResult_t HmmHelpers::getAlphaAndBeta(int32_t numObs,const HmmDataVec_t & pi, const HmmDataMatrix_t & logbmap, const HmmDataMatrix_t & A,const uint32_t numStates,const LabelMap_t & labels, const TransitionMultiMap_t & forbiddenTransitions) {
    (void)getLabel;

    /*
     Calculates 'alpha' the forward variable.
     
     The alpha variable is a numpy array indexed by time, then state (NxT).
     alpha[i][t] = the probability of being in state 'i' after observing the
     first t symbols.
     
     forbidden transitions means at that time index a transition is unavailable
     labels mean that you have to be in that time
     */
    
    int t,j,i;
    HmmDataMatrix_t logalpha = getLogZeroedMatrix(numStates,numObs);
    HmmDataMatrix_t logbeta = getLogZeroedMatrix(numStates,numObs);
    HmmFloat_t temp;
    HmmDataMatrix_t A2 = A; //copy
    
    //nominal A matrix
    for (j = 0; j < numStates; j++) {
        for (i = 0; i < numStates; i++) {
            A2[j][i] = eln(A2[j][i]);
        }
    }
    
    const HmmDataMatrix_t logA = A2;
    
    //init stage - alpha_1(x) = pi(x)b_x(O1)
    
    for (j = 0; j < numStates; j++) {
        logalpha[j][0] = elnproduct(eln(pi[j]), logbmap[j][0]);
    }
    
    
    for (t = 1; t < numObs; t++) {
        
        for (j = 0; j < numStates; j++) {
            temp = LOGZERO;
            
            for (i = 0; i < numStates; i++) {
                //alpha[j][t] += alpha[i][t-1]*A[i][j];
                const HmmFloat_t tempval = elnproduct(logalpha[i][t-1],logA[i][j]);
                temp = elnsum(temp,tempval);
            }
            
            //alpha[j][t] *= bmap[j][t];
            logalpha[j][t] = elnproduct(temp, logbmap[j][t]);
        }
        
        
        uint32_t label;
        if (getLabel(label,t,labels)) {
            for (j = 0; j < numStates; j++) {
                if (j != label) {
                    logalpha[j][t] = NON_LABEL_PENALTY;
                }
            }
        }
        
        
    }
    
    /*
     Calculates 'beta' the backward variable.
     
     The beta variable is a numpy array indexed by time, then state (NxT).
     beta[i][t] = the probability of being in state 'i' and then observing the
     symbols from t+1 to the end (T).
     */
    
    
    // init stage
    for (int s = 0; s < numStates; s++) {
        logbeta[s][numObs - 1] = 0.0;
    }
    
    
    
    for (t = numObs - 2; t >= 0; t--) {
        
        for (i = 0; i < numStates; i++) {
            temp = LOGZERO;
            for (j = 0;  j < numStates; j++) {
                const HmmFloat_t tempval  = elnproduct(logbmap[j][t+1], logbeta[j][t+1]);
                const HmmFloat_t tempval2 = elnproduct(tempval, logA[i][j]);
                temp = elnsum(temp,tempval2);
                //beta[i][t] += A[i][j]*bmap[j][t+1] * beta[j][t+1];
            }
            
            logbeta[i][t] = temp;
        }
        
        
        uint32_t label;
        if (getLabel(label,t,labels)) {
            for (j = 0; j < numStates; j++) {
                if (j != label) {
                    logbeta[j][t] = NON_LABEL_PENALTY;
                }
            }
        }
        
    }
    
    temp = LOGZERO;
    for (i = 0; i < numStates; i++) {
        temp = elnsum(temp,logalpha[i][numObs-1]);
    }
    
    
    const AlphaBetaResult_t result(logalpha,logbeta,logA,temp);
    
    return result;
    

    
}

AlphaBetaResult_t HmmHelpers::getAlphaAndBeta(int32_t numObs,const HmmDataVec_t & pi, const HmmDataMatrix_t & logbmap, const HmmDataMatrix_t & A, const uint32_t numStates) {
    
    //pass empty structures
    LabelMap_t labels;
    TransitionMultiMap_t forbiddenTransitions;
    
    return getAlphaAndBeta(numObs, pi, logbmap, A, numStates, labels, forbiddenTransitions);
    
}

Hmm3DMatrix_t HmmHelpers::getLogXi(const AlphaBetaResult_t & alphabeta,const HmmDataMatrix_t & logbmap, const uint32_t numObs,const uint32_t numStates) {

    TransitionMultiMap_t forbiddenTransitions;

    return getLogXi(alphabeta, logbmap, forbiddenTransitions, numObs,numStates);
}

Hmm3DMatrix_t HmmHelpers::getLogXi(const AlphaBetaResult_t & alphabeta,const HmmDataMatrix_t & logbmap,const TransitionMultiMap_t & forbiddenTransitions, const uint32_t numObs,const uint32_t numStates) {
    /*
     Calculates 'xi', a joint probability from the 'alpha' and 'beta' variables.
     
     The xi variable is a numpy array indexed by time, state, and state (TxNxN).
     xi[t][i][j] = the probability of being in state 'i' at time 't', and 'j' at
     time 't+1' given the entire observation sequence.
     */
    int32_t t,i,j;
    
    const HmmDataMatrix_t & logalpha = alphabeta.logalpha;
    const HmmDataMatrix_t & logbeta = alphabeta.logbeta;
    const HmmDataMatrix_t & logA = alphabeta.logA;
    Hmm3DMatrix_t logxi = getLogZeroed3dMatrix(numStates,numStates, numObs);
    HmmDataVec_t tempvec = getZeroedVec(numStates);
    HmmDataVec_t logdenomvec = getZeroedVec(numStates);
    HmmFloat_t normalizer;
    
    for (t = 0; t < numObs - 1; t++) {
        normalizer = LOGZERO;
        
        HmmDataMatrix_t logAThisTimeStep = getLogAWithForbiddenStates(logA,forbiddenTransitions,t);

        for (i = 0; i < numStates; i++) {
            for (j = 0; j < numStates; j++) {
                
                const HmmFloat_t tempval1 = elnproduct(logalpha[i][t], logAThisTimeStep[i][j]);
                const HmmFloat_t tempval2 = elnproduct(logbmap[j][t+1], logbeta[j][t+1]);
                const HmmFloat_t tempval3 = elnproduct(tempval1,tempval2);
                
                logxi[i][j][t] = tempval3;
                
                normalizer = elnsum(tempval3, normalizer);
            }
        }
        
        
        for (i = 0; i < numStates; i++) {
            for (j = 0; j < numStates; j++) {
                logxi[i][j][t] = elnproduct(logxi[i][j][t], -normalizer);
            }
        }
    }
    
    return logxi;
    
}



HmmDataMatrix_t HmmHelpers::getLogBMap(const ModelVec_t & models, const HmmDataMatrix_t & meas) {
    HmmDataMatrix_t logbmap;
    
    
    for (ModelVec_t::const_iterator it = models.begin(); it != models.end(); it++) {
        const HmmPdfInterface * ref = (*it).get();
        logbmap.push_back(ref->getLogOfPdf(meas));
    }
    
    return logbmap;
}

HmmDataMatrix_t HmmHelpers::getLogGamma(const AlphaBetaResult_t & alphabeta,uint32_t numObs, uint32_t numStates) {
    /*
     Calculates 'gamma' from xi.
     
     Gamma is a (TxN) numpy array, where gamma[t][i] = the probability of being
     in state 'i' at time 't' given the full observation sequence.
     */
    
    int32_t t,i;
    HmmFloat_t normalizer;
    HmmFloat_t temp;
    HmmDataMatrix_t loggamma = getLogZeroedMatrix(numStates, numObs);
    
    for (t = 0; t < numObs; t++) {
        normalizer = LOGZERO;
        for (i = 0; i < numStates; i++) {
            temp = elnproduct(alphabeta.logalpha[i][t], alphabeta.logbeta[i][t]);
            loggamma[i][t] = temp;
            normalizer = elnsum(normalizer, temp);
        }
        
        
        for (i = 0; i < numStates; i++) {
            loggamma[i][t] = elnproduct(loggamma[i][t], -normalizer);
        }
    }
    
    return loggamma;
    
}

HmmDataMatrix_t HmmHelpers::reestimateA(const HmmDataMatrix_t & A, const Hmm3DMatrix_t & logxi, const HmmDataMatrix_t & loggamma,const size_t numObs,const HmmFloat_t damping, const HmmFloat_t minValueForA, const uint32_t numStates) {
    
    int32_t i,j,t;
    HmmDataMatrix_t A2 = getZeroedMatrix(numStates, numStates);
    
    for (i = 0; i < numStates; i++) {
        HmmFloat_t denom = LOGZERO;
        
        for (t = 0; t < numObs; t++) {
            denom = elnsum(denom, loggamma[i][t]) ;
        }
        
        for (j = 0; j < numStates; j++) {
            HmmFloat_t numer = LOGZERO;
            for (t = 0; t < numObs; t++) {
                numer = elnsum(numer,logxi[i][j][t]);
            }
            
            A2[i][j] = eexp(elnproduct(numer, -denom));
            
            if (A[i][j] > EPSILON) {
                if (A2[i][j] <= minValueForA) {
                    A2[i][j] = minValueForA;
                }
            }
        }
    }
    
    
    for (j = 0; j < numStates; j++) {
        for (i = 0; i < numStates; i++) {
            A2[j][i] = damping * A2[j][i] + (1.0 - damping) * A[j][i];
        }
    }
    
    for (j = 0; j < numStates; j++) {
        HmmFloat_t sum = 0.0;
        for (i = 0; i < numStates; i++) {
            sum += A2[j][i];
        }
        
        if (sum < EPSILON) {
            continue;
        }
        
        for (i = 0; i < numStates; i++) {
            A2[j][i] /= sum;
        }
    }
    
    for (j = 0; j < numStates; j++) {
        for (i = 0; i < numStates; i++) {
            
            if (A2[j][i] > EPSILON) {
                if (A2[j][i] <= minValueForA) {
                    A2[j][i] = minValueForA;
                }
                
                if (A2[j][i] > minValueForA) {
                    A2[j][i] = minValueForA;
                }
            }
            
        }
    }
    
    return A;
    
}


HmmDataMatrix_t HmmHelpers::getLogANumerator(const HmmDataMatrix_t & originalA, const AlphaBetaResult_t & alphabeta,const HmmDataMatrix_t & logbmap,const TransitionMultiMap_t & forbiddenTransitions,const size_t numObs, const uint32_t numStates) {
    
    int32_t i,j,t;
    HmmDataMatrix_t logANumerator = getLogZeroedMatrix(numStates, numStates);
    
    const HmmDataMatrix_t & logalpha = alphabeta.logalpha;
    const HmmDataMatrix_t & logbeta = alphabeta.logbeta;
    const HmmDataMatrix_t & logA = alphabeta.logA;
    
    
    for (i = 0; i < numStates; i++) {
        for (j = 0; j < numStates; j++) {
            HmmFloat_t numer = LOGZERO;
            
            for (t = 0; t < numObs - 1; t++) {
                HmmDataMatrix_t logAThisTimeStep = getLogAWithForbiddenStates(logA,forbiddenTransitions,t);
                
                const HmmFloat_t tempval1 = elnproduct(logalpha[i][t], logAThisTimeStep[i][j]);
                const HmmFloat_t tempval2 = elnproduct(logbmap[j][t+1], logbeta[j][t+1]);
                const HmmFloat_t tempval3 = elnproduct(tempval1,tempval2);
                
                numer = elnsum(numer,tempval3);
            }
            
            if (originalA[i][j] == 0.0) {
                logANumerator[i][j] = LOGZERO;
            }
            else {
                logANumerator[i][j] = numer;
            }
        }
    }
    
    
    
    for (i = 0; i < numStates; i++) {
        for (j = 0; j < numStates; j++) {
            logANumerator[j][i] = elnproduct(logANumerator[j][i], -alphabeta.logmodelcost);
        }
    }
    
    
    return logANumerator;
    
}

HmmDataMatrix_t HmmHelpers::getLogAlphabetNumerator(const AlphaBetaResult_t & alphabeta, const HmmDataVec_t & rawdata, const uint32_t numStates, const uint32_t numObs, const uint32_t alphabetSize ) {
    
    int32_t iState,iAlphabet,t;

    HmmDataMatrix_t logAlphabetNumerator = getLogZeroedMatrix(numStates, alphabetSize);

    const HmmDataMatrix_t & logalpha = alphabeta.logalpha;
    const HmmDataMatrix_t & logbeta = alphabeta.logbeta;
    
    for (iState = 0; iState < numStates; iState++) {
       
        for (t = 0; t < numObs; t++) {
            const uint32_t idx = (uint32_t)rawdata[t];
            
            assert(idx >= 0 && idx < alphabetSize);
            
            logAlphabetNumerator[iState][idx] = elnsum(logAlphabetNumerator[iState][idx] ,elnproduct(logalpha[iState][t], logbeta[iState][t]));
        }

    }

    
    for (iState = 0; iState < numStates; iState++) {
        for (iAlphabet = 0; iAlphabet < alphabetSize; iAlphabet++) {
            logAlphabetNumerator[iState][iAlphabet] = elnproduct(logAlphabetNumerator[iState][iAlphabet], -alphabeta.logmodelcost);
        }
    }
    
    return logAlphabetNumerator;


}


HmmDataVec_t HmmHelpers::getLogDenominator(const AlphaBetaResult_t & alphabeta, const uint32_t numStates, const uint32_t numObs) {
    
    int32_t iState,t;
    
    HmmDataVec_t logDenominator = getLogZeroedVec(numStates);
    
    const HmmDataMatrix_t & logalpha = alphabeta.logalpha;
    const HmmDataMatrix_t & logbeta = alphabeta.logbeta;
    
    for (iState = 0; iState < numStates; iState++) {
        for (t = 0; t < numObs; t++) {
            logDenominator[iState] = elnsum(logDenominator[iState],elnproduct(logalpha[iState][t], logbeta[iState][t]));
        }
        
        logDenominator[iState] = elnproduct(logDenominator[iState], -alphabeta.logmodelcost);
    }
    
    return logDenominator;
}

HmmDataMatrix_t HmmHelpers::elnMatrixScalarProduct(const HmmDataMatrix_t & m1, const HmmFloat_t a) {
    const int m = m1.size();
    const int n = m1[0].size();
    
    HmmDataMatrix_t m3 = getZeroedMatrix(m, n);
    HmmFloat_t elnA = (eln(a));
    for (int j = 0; j < m; j++) {
        for (int i = 0; i < n; i++) {
            m3[j][i] = elnproduct(m1[j][i], elnA);
        }
    }
    
    return m3;
}

HmmDataVec_t HmmHelpers::elnVectorScalarProduct(const HmmDataVec_t & m1, const HmmFloat_t a) {
    const int m = m1.size();
    
    HmmDataVec_t m3 = getZeroedVec(m);
    HmmFloat_t elnA = (eln(a));
    for (int j = 0; j < m; j++) {
        m3[j] = elnproduct(m1[j], elnA);
    }
    
    return m3;
}

HmmDataMatrix_t HmmHelpers::elnAddMatrix(const HmmDataMatrix_t & m1, const HmmDataMatrix_t & m2) {
    const int m = m1.size();
    const int n = m1[0].size();
    
    HmmDataMatrix_t m3 = getZeroedMatrix(m, n);
    
    for (int j = 0; j < m; j++) {
        for (int i = 0; i < n; i++) {
            m3[j][i] = elnsum(m1[j][i], m2[j][i]);
        }
    }
    
    return m3;
}

HmmDataVec_t HmmHelpers::elnAddVector(const HmmDataVec_t & m1, const HmmDataVec_t & m2) {
    const int m = m1.size();
    
    HmmDataVec_t m3 = getZeroedVec(m);
    
    for (int j = 0; j < m; j++) {
        m3[j] = elnsum(m1[j], m2[j]);
        
    }
    
    return m3;
}


static ViterbiPath_t decodePath(int32_t startidx,const ViterbiPathMatrix_t & paths) {
    size_t len = paths[0].size();
    
    
    ViterbiPath_t path;
    path.resize(len);
    
    path[len-1] = startidx;
    for(int i = len - 2; i >= 0; i--) {
        path[i] = paths[path[i+1]][i];
    }
    
    
    return path;
}

static ViterbiDecodeResult_t decodePathAndGetCost(int32_t startidx,const ViterbiPathMatrix_t & paths,const HmmDataMatrix_t & phi)  {
    
    const size_t len = paths[0].size();
    
    
    //get viterbi path
    ViterbiPath_t path = decodePath(startidx,paths);
    
    //compute cost stuff
    const HmmFloat_t cost = phi[path[len-1]][len-1];
    
    //really -bic
//    const HmmFloat_t bic = 2*cost - _alphabetNumerator[0].size() * _numStates * log(len);
    
    return ViterbiDecodeResult_t(path,cost,cost);
}


ViterbiDecodeResult_t HmmHelpers::decodeWithoutLabels(const HmmDataMatrix_t & A, const HmmDataMatrix_t & logbmap, const HmmDataVec_t & pi, const TransitionMultiMap_t & forbiddenTransitions,const uint32_t numStates,const uint32_t numObs) {
    int j,i,t;

    HmmDataVec_t costs;
    costs.resize(numStates);
    
    HmmDataMatrix_t phi = getLogZeroedMatrix(numStates, numObs);
    ViterbiPathMatrix_t vindices = getZeroedPathMatrix(numStates, numObs);
    HmmDataMatrix_t logA = getELNofMatrix(A);
    
    //init
    for (i = 0; i < numStates; i++) {
        phi[i][0] = elnproduct(logbmap[i][0], eln(pi[i]));
    }
    
    for (t = 1; t < numObs; t++) {
        
        HmmDataMatrix_t logAThisIndex = getLogAWithForbiddenStates(logA, forbiddenTransitions, t);

        
        for (j = 0; j < numStates; j++) {
            const HmmFloat_t obscost = logbmap[j][t];
            
            for (i = 0; i < numStates; i++) {
                costs[i] = elnproduct(logAThisIndex[i][j], obscost);
            }
            
            for (i = 0; i < numStates; i++) {
                costs[i] = elnproduct(costs[i], phi[i][t-1]);
            }
            
            const int32_t maxidx = getArgMaxInVec(costs);
            const HmmFloat_t maxval = costs[maxidx];
            
            phi[j][t] = maxval;
            vindices[j][t] = maxidx;
        }
    }
    
    const ViterbiDecodeResult_t result = decodePathAndGetCost(A.size() - 1, vindices, phi);
    
    
    return result;
    
}

ViterbiDecodeResult_t HmmHelpers::decodeWithMinimumDurationConstraints(const HmmDataMatrix_t & A, const HmmDataMatrix_t & logbmap, const HmmDataVec_t & pi, const TransitionMultiMap_t & forbiddenTransitions,const UIntVec_t & durationMinimums,const uint32_t numStates,const uint32_t numObs) {
    
    
    int j,i,t;
    
    HmmDataVec_t costs;
    costs.resize(numStates);
    
    HmmDataMatrix_t phi = getLogZeroedMatrix(numStates, numObs);
    ViterbiPathMatrix_t vindices = getZeroedPathMatrix(numStates, numObs);
    HmmDataMatrix_t logA = getELNofMatrix(A);
    
    UIntVec_t zeta; //this is the count for how long you've been in the same state
    //see the paper "Long-term Activities Segmentation using Viterbi Algorithm with a k-minimum-consecutive-states Constraint"
    //by Enrique Garcia-Ceja, Ramon Brena, 2014
    
    zeta.resize(numStates);
    for (i = 0; i < numStates; i++) {
        zeta[i] = 1;
    }
    
    //init
    for (i = 0; i < numStates; i++) {
        phi[i][0] = elnproduct(logbmap[i][0], eln(pi[i]));
    }
    
    for (t = 1; t < numObs; t++) {
        
        HmmDataMatrix_t logAThisIndex = getLogAWithForbiddenStates(logA, forbiddenTransitions, t);
        
        
        for (j = 0; j < numStates; j++) {
            
            const HmmFloat_t obscost = logbmap[j][t];
            
            for (i = 0; i < numStates; i++) {
                costs[i] = elnproduct(logAThisIndex[i][j], obscost);
            }
            
            for (i = 0; i < numStates; i++) {
                costs[i] = elnproduct(costs[i], phi[i][t-1]);
            }
            
            int32_t maxidx = j;
            HmmFloat_t maxval = costs[j];
            
            if (j == 1 && t == 61) {
                int foo = 3;
                foo++;
            }
            
            if (j == 1) {
                int foo = 3;
                foo++;
            }
            
            if (j == 2) {
                int foo = 3;
                foo++;
            }
            
            if (zeta[j] >= durationMinimums[maxidx]) {
                //sorted ascending
                auto indices = sort_indexes(costs);
                bool worked = false;
                for (int32_t maxii = numStates - 1; maxii >= 0; maxii--) {
                    maxidx = indices[maxii];
                    maxval = costs[maxidx];
                    
                    //have we been in the old state long enough to switch?
                    if (zeta[maxidx] >= durationMinimums[maxidx] && maxval > LOGZERO) {
                        worked = true;
                        break;
                    }
                }
                
                if (!worked) {
                    maxidx = j;
                    maxval = costs[j];
                }
            }
            
            
            //best path is to stay?  increment zeta.
            if (maxidx == j) {
                zeta[j] += 1;
            }
            else {
                zeta[j] = 1;
            }
            
            phi[j][t] = maxval;
            vindices[j][t] = maxidx;
        }
    }
    
    const ViterbiDecodeResult_t result = decodePathAndGetCost(A.size() - 1, vindices, phi);
    
    
    return result;

    
}



UIntVec_t HmmHelpers::getVecFromLabels(const LabelMap_t & labels, const uint32_t end,const uint32_t nolabellabel) {
    UIntVec_t vec;
    vec.reserve(end);
    for (uint32_t t = 0; t < end; t++) {
        LabelMap_t::const_iterator it = labels.find(t);
        
        if (it != labels.end()) {
            vec.push_back((*it).second);
        }
        else {
            vec.push_back(nolabellabel);
        }
    }
    
    return vec;
}



TransitionAtTime_t HmmHelpers::getPathTransitions(const ViterbiPath_t & path) {
    TransitionAtTime_t results;
    for (int t = 1; t < path.size(); t++) {
        if (path[t] != path[t - 1]) {
            results.insert(std::make_pair (StateIdxPair(path[t - 1],path[t]),t));
        }
    }
    
    return results;
}

TransitionAtTime_t HmmHelpers::getLabelTransitions(const LabelMap_t & labels, const uint32_t end) {
    uint32_t prev = 0xFFFFFFFF;
    TransitionAtTime_t results;
    for (uint32_t t = 0; t < end; t++) {
        LabelMap_t::const_iterator it = labels.find(t);
        
        if (it != labels.end()) {
            const uint32_t current  = (*it).second;
            
            if (current != prev && prev != 0xFFFFFFFF) {
                results.insert(std::make_pair (StateIdxPair(prev,current),t));
            }
            
            prev = (*it).second;
        }
        else {
            prev = 0xFFFFFFFF;
        }
    }
    
    return results;
}

void HmmHelpers::printTransitions(const ViterbiPath_t & path) {
    const TransitionAtTime_t pt = getPathTransitions(path);
    
    for (auto it = pt.begin(); it != pt.end(); it++) {
        StateIdxPair transition = (*it).first;
        std::cout << "PAIR: " << transition.from << "," << transition.to << "," << (*it).second << std::endl;
        int32_t t = (*it).second;
        t -= 1;
        int hour = t * 5.0 / 60.0;
        int min = t * 5.0 - hour * 60.0;
        hour += 20;
        
        if (hour >= 24) {
            hour -= 24;
        }
        
        
        char buf[16];
        snprintf(buf, 16, "%02d:%02d",hour,min);
        
        std::cout << transition.from << " ---> " << transition.to << " at time " << buf << std::endl;
    }
    
    std::cout << "----------" << std::endl;
}


TransitionAtTime_t HmmHelpers::evalLabels(TransitionAtTime_t & counts, const LabelMap_t & labels, const ViterbiPath_t & path) {
    const TransitionAtTime_t lt = getLabelTransitions(labels,path.size());
    const TransitionAtTime_t pt = getPathTransitions(path);
    TransitionAtTime_t results;
    
    for (auto it = lt.begin(); it != lt.end(); it++) {
        auto it2 = pt.find((*it).first);
        auto itCounts = counts.find((*it).first);
        
        if (itCounts == counts.end()) {
            counts.insert(std::make_pair((*it).first,0));
        }
        
        counts[(*it).first]++;
        
        if (it2 == pt.end()) {
            continue;
        }
        
        const int32_t dt = (*it2).second - (*it).second;
        
        results.insert(std::make_pair((*it).first,dt));
    }
    
    return results;
    
}



void HmmHelpers::updateConfusionCount(const LabelMap_t & labels,const ViterbiPath_t & path,HmmDataMatrix_t & confusionMatrix) {
    
    for (uint32_t t = 0; t < path.size(); t++) {
        LabelMap_t::const_iterator it = labels.find(t);
        
        if (it != labels.end()) {
            uint32_t label = (*it).second;
            uint32_t prediction = path[t];
            
            confusionMatrix[prediction][label] += 1.0;
        }
    }
}


