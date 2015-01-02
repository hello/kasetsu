'''
Created on Oct 31, 2012

@author: GuyZ

This code is based on:
 - QSTK's HMM implementation - http://wiki.quantsoftware.org/
 - A Tutorial on Hidden Markov Models and Selected Applications in Speech Recognition, LR RABINER 1989 
'''

import numpy
import pylab 
import copy


k_max_depth = 10
#k_percentage_of_best_cutoff = 0.02
k_cost_budget = 3.0
k_max_paths = 2048
k_nbest_in_branch = 10

class _BaseHMM(object):
    '''
    Implements the basis for all deriving classes, but should not be used directly.
    '''
    
    def __init__(self,n,m,precision=numpy.double,verbose=False):
        self.n = n
        self.m = m
        
        self.precision = precision
        self.verbose = verbose
        self._eta = self._eta1
        
    def _eta1(self,t,T):
        '''
        Governs how each sample in the time series should be weighed.
        This is the default case where each sample has the same weigh, 
        i.e: this is a 'normal' HMM.
        '''
        return 1.
      
    def forwardbackward(self,observations, cache=False):
        '''
        Forward-Backward procedure is used to efficiently calculate the probability of the observation, given the model - P(O|model)
        alpha_t(x) = P(O1...Ot,qt=Sx|model) - The probability of state x and the observation up to time t, given the model.
        
        The returned value is the log of the probability, i.e: the log likehood model, give the observation - logL(model|O).
        
        In the discrete case, the value returned should be negative, since we are taking the log of actual (discrete)
        probabilities. In the continuous case, we are using PDFs which aren't normalized into actual probabilities,
        so the value could be positive.
        '''
        if (cache==False):
            self._mapB(observations)
        
        alpha, c = self._calcalpha(observations)
        return numpy.sum(numpy.log(c))
    
    def _calcalpha(self,observations):
        '''
        Calculates 'alpha' the forward variable.
    
        The alpha variable is a numpy array indexed by time, then state (TxN).
        alpha[t][i] = the probability of being in state 'i' after observing the 
        first t symbols.
        '''        
        alpha = numpy.zeros((len(observations),self.n),dtype=self.precision)
        c = numpy.ones((len(observations), ))
        
        # init stage - alpha_1(x) = pi(x)b_x(O1)
        for x in xrange(self.n):
            alpha[0][x] = self.pi[x]*self.B_map[x][0]
        
        # induction
        for t in xrange(1,len(observations)):
            for j in xrange(self.n):
                for i in xrange(self.n):
                    alpha[t][j] += alpha[t-1][i]*self.A[i][j]
                
                alpha[t][j] *= self.B_map[j][t]
                
            c[t] = numpy.sum(alpha[t][:])
                
            alpha[t][:] = alpha[t][:] / c[t] 
                
        return (alpha, c)

    def evaluate_path_cost(self, observations, path, numobs):
        self._mapB(observations)
        p = numpy.zeros((numobs, ))
        
        p[0] = -numpy.log(self.B_map[path[0]][0] + 1e-15) - numpy.log(self.pi[0] + 1e-15)
        
        for t in xrange(1, numobs):
            istate = path[t-1]
            istate2 = path[t]
            ptransition = self.A[istate, istate2]
            pobs = self.B_map[path[t]][t]
            
            p[t] = p[t - 1] - numpy.log(ptransition + 1e-15) - numpy.log(pobs + 1e-15)
            
        return p

    def _calcbeta(self,observations, c):
        '''
        Calculates 'beta' the backward variable.
        
        The beta variable is a numpy array indexed by time, then state (TxN).
        beta[t][i] = the probability of being in state 'i' and then observing the
        symbols from t+1 to the end (T).
        '''        
        beta = numpy.zeros((len(observations),self.n),dtype=self.precision)
        
        # init stage
        for s in xrange(self.n):
            beta[len(observations)-1][s] = 1.
        
        # induction
        for t in xrange(len(observations)-2,-1,-1):
            for i in xrange(self.n):
                for j in xrange(self.n):
                    beta[t][i] += self.A[i][j]*self.B_map[j][t+1]*beta[t+1][j]
                    
                
            beta[t][:] = beta[t][:] / c[t]    
        
        return beta
    
    def decode(self, observations, npadding=0):
        '''
        Find the best state sequence (path), given the model and an observation. i.e: max(P(Q|O,model)).
        
        This method is usually used to predict the next state after training. 
        '''        
        # use Viterbi's algorithm. It is possible to add additional algorithms in the future.
        return self._viterbi(observations, len(observations), npadding)
    
    #given original viterbi path, deviate from it
    #starting at tstart, and moving towards the max incming in state idxstart at that time
    def _backtrace_viterbi_path(self, viterbi_path, vi, tstart, idxstart):
        path = copy.deepcopy(viterbi_path)
        state = idxstart
        for t in xrange(tstart-1, -1, -1):
            path[t] = state
            state = vi[state][t-1]
            
        return path
        
    def _get_second_best_path_costs(self,depth, path_dict, path,viterbi_info):
        
        viterbi_path, vi, viterbi_pathcost, phi, npadding = viterbi_info
        numobs = len(viterbi_path)
        second_best_merge_from_idx = numpy.zeros((numobs, )).astype(int)
        second_best_costs = numpy.zeros((numobs, ))
        
        #just start and end at state zero
        second_best_costs[0] = phi[0][0]
        
        #phi2(path[t][t]) = min [ phi2(path[t-1][t-1])  + cost[path[t-1][path[t]]; 
        #                         min( phi[j][t-1] + cost[j][path[t]] j != path[t-1]
        cost = numpy.zeros((self.n, ))
        
        for t in xrange(1, numobs):
            j = path[t]
            
            obscost = -numpy.log(self.B_map[j][t] + 1e-15)
                
            for i in xrange(self.n): #i means the incoming from ith hidden state
                #compute incoming costs
                
                pc = -numpy.log(self.A[i][j] + 1e-15) + obscost
                minval = float("Inf")
                minidx = -1
                #if incoming state is not the previous viterbi path
                if i != path[t-1]:
                    cost = pc + phi[i][t-1]
                    if cost < minval:
                        minidx = i;
                        minval = cost
               

            second_best_costs[t] = minval
            second_best_merge_from_idx[t] = minidx
        
        final_viterbi_cost = viterbi_pathcost[-1]
        remaining_costs = final_viterbi_cost - viterbi_pathcost
        second_best_costs =  second_best_costs + remaining_costs
        
        cost_idx = numpy.argsort(second_best_costs)
        
        paths = []
        
        
        count = 0
        for cidx in cost_idx:
            
            if cidx < npadding:
                continue
            
            cost = second_best_costs[cidx]
            statestart = second_best_merge_from_idx[cidx]
            
            costdiff = cost - final_viterbi_cost
            relcost = costdiff / final_viterbi_cost
            
            if count > k_nbest_in_branch:
                break;
                        
            #if  relcost < k_percentage_of_best_cutoff: #within x% of original best cost
            if costdiff < k_cost_budget:
                #get new path (merged at min index)
                newpath = self._backtrace_viterbi_path(path, vi, cidx, statestart)
                
                #check to see if we have already found this path by hashing the path
                v = tuple(newpath.tolist())
                if not path_dict.has_key(v):
                    count = count + 1

                    #found too many?  oh god, stop it all
                    if len(path_dict) >= k_max_paths:
                        return
                        
                    #add new path because it's unique
                    path_dict[v] = cost
                    paths.append(newpath)
            else:
                break

        if depth > 0:
            for p in paths:
                self._get_second_best_path_costs(depth-1, path_dict, p,viterbi_info)
        
    def _viterbi(self, observations, numobs, npadding):
        '''
        Find the best state sequence (path) using viterbi algorithm - a method of dynamic programming,
        very similar to the forward-backward algorithm, with the added step of maximization and eventual
        backtracing.
        
        delta[t][i] = max(P[q1..qt=i,O1...Ot|model] - the path ending in Si and until time t,
        that generates the highest probability.
        
        psi[t][i] = argmax(delta[t-1][i]*aij) - the index of the maximizing state in time (t-1), 
        i.e: the previous state.
        '''
        # similar to the forward-backward algorithm, we need to make sure that we're using fresh data for the given observations.
        self._mapB(observations)
        
        phi = numpy.zeros((self.n,numobs),dtype=self.precision)
        viterbi_indices = numpy.zeros((self.n, numobs)).astype(int)
        mergecount = numpy.zeros((numobs, ))
        
        # init 
        for i in xrange(self.n):
            phi[i][:] = -numpy.log(self.pi[i]+1e-15) - numpy.log(self.B_map[i][0] + 1e-15)
      
      
        #do viterbi
        cost = numpy.zeros((self.n, ))
        pathcost = numpy.zeros((numobs, ))
        for t in xrange(1, numobs):
            for j in xrange(self.n): #"j" mean THIS (the jth) hidden state
                obscost = -numpy.log(self.B_map[j][t] + 1e-15)
                
                for i in xrange(self.n): #i means the incoming from ith hidden state
                    #compute incoming costs
                    cost[i] = -numpy.log(self.A[i][j] + 1e-15) + obscost 
                
                
                for i in xrange(self.n): 
                    cost[i] = cost[i] + phi[i][t-1]
                    
                minidx = numpy.argmin(cost)
                minval = cost[minidx]
                pathcost[t] = minval
                
                phi[j][t] = minval
                viterbi_indices[j][t] = minidx
       
        path = numpy.zeros((numobs, )).astype(int)
        #let's just say you wind up in state zero at the end? 
        path[numobs-1] = 0
        

        #backtrack to get optimal path
        for t in xrange(numobs - 2, -1, -1):
            path[t] = viterbi_indices[path[t+1]][t]
               
        viterbi_info = path, viterbi_indices, pathcost, phi, npadding
        
        path_dict = {}
        v = tuple(path.tolist())
        path_dict[v] = 0.0
        
        #recursive
        self._get_second_best_path_costs(k_max_depth, path_dict, path,viterbi_info)
        
        return path_dict
     
    def _calcxi(self,observations,alpha=None,beta=None):
        '''
        Calculates 'xi', a joint probability from the 'alpha' and 'beta' variables.
        
        The xi variable is a numpy array indexed by time, state, and state (TxNxN).
        xi[t][i][j] = the probability of being in state 'i' at time 't', and 'j' at
        time 't+1' given the entire observation sequence.
        '''        
        alpha, c = self._calcalpha(observations)
        beta = self._calcbeta(observations, c)
        xi = numpy.zeros((len(observations),self.n,self.n),dtype=self.precision)
        
        for t in xrange(len(observations)-1):
            denom = 0.0
            for i in xrange(self.n):
                for j in xrange(self.n):
                    thing = 1.0
                    thing *= alpha[t][i]
                    thing *= self.A[i][j]
                    thing *= self.B_map[j][t+1]
                    thing *= beta[t+1][j]
                    denom += thing
                    

            for i in xrange(self.n):
                for j in xrange(self.n):
                    numer = 1.0
                    numer *= alpha[t][i]
                    numer *= self.A[i][j]
                    numer *= self.B_map[j][t+1]
                    numer *= beta[t+1][j]
                    
                    xi[t][i][j] = numer/denom
        
        return xi

    def _calcgamma(self,xi,seqlen):
        '''
        Calculates 'gamma' from xi.
        
        Gamma is a (TxN) numpy array, where gamma[t][i] = the probability of being
        in state 'i' at time 't' given the full observation sequence.
        '''        
        gamma = numpy.zeros((seqlen,self.n),dtype=self.precision)
        
        for t in xrange(seqlen):
            for i in xrange(self.n):
                gamma[t][i] = sum(xi[t][i])
        
        
        return gamma
    
    def train(self, observations, iterations=1,epsilon=0.0001,thres=-0.001):
        '''
        Updates the HMMs parameters given a new set of observed sequences.
        
        observations can either be a single (1D) array of observed symbols, or when using
        a continuous HMM, a 2D array (matrix), where each row denotes a multivariate
        time sample (multiple features).
        
        Training is repeated 'iterations' times, or until log likelihood of the model
        increases by less than 'epsilon'.
        
        'thres' denotes the algorithms sensitivity to the log likelihood decreasing
        from one iteration to the other.
        '''        
        self._mapB(observations)
        
        for i in xrange(iterations):
            prob_old, prob_new = self.trainiter(observations)

            if (self.verbose):      
                print "iter: ", i, ", L(model|O) =", prob_old, ", L(model_new|O) =", prob_new, ", converging =", ( prob_new-prob_old > thres )
                
            #if ( abs(prob_new-prob_old) < epsilon ):
            #    # converged
            #    break
                
    def _updatemodel(self,new_model):
        '''
        Replaces the current model parameters with the new ones.
        '''
        self.pi = new_model['pi']
        self.A = new_model['A']
                
    def trainiter(self,observations):
        '''
        A single iteration of an EM algorithm, which given the current HMM,
        computes new model parameters and internally replaces the old model
        with the new one.
        
        Returns the log likelihood of the old model (before the update),
        and the one for the new model.
        '''        
        # call the EM algorithm
        new_model = self._baumwelch(observations)
        
        # calculate the log likelihood of the previous model
        prob_old = self.forwardbackward(observations, cache=True)
        
        # update the model with the new estimation
        self._updatemodel(new_model)
        
        # calculate the log likelihood of the new model. Cache set to false in order to recompute probabilities of the observations give the model.
        prob_new = self.forwardbackward(observations, cache=False)
        
        return prob_old, prob_new
    
    def _reestimateA(self,observations,xi,gamma):
        '''
        Reestimation of the transition matrix (part of the 'M' step of Baum-Welch).
        Computes A_new = expected_transitions(i->j)/expected_transitions(i)
        
        Returns A_new, the modified transition matrix. 
        '''
        A_new = numpy.zeros((self.n,self.n),dtype=self.precision)
        for i in xrange(self.n):
            for j in xrange(self.n):
                numer = 0.0
                denom = 0.0
                for t in xrange(len(observations)-1):
                    numer += (self._eta(t,len(observations)-1)*xi[t][i][j])
                    denom += (self._eta(t,len(observations)-1)*gamma[t][i])
                A_new[i][j] = numer/denom
        return A_new
    
    def _calcstats(self,observations):
        '''
        Calculates required statistics of the current model, as part
        of the Baum-Welch 'E' step.
        
        Deriving classes should override (extend) this method to include
        any additional computations their model requires.
        
        Returns 'stat's, a dictionary containing required statistics.
        '''
        stats = {}
        
        alpha, c = self._calcalpha(observations)
        beta = self._calcbeta(observations, c)
        
        stats['loglik'] = numpy.sum(numpy.log(c))
        stats['lik'] = numpy.exp(stats['loglik'])
        
        stats['alpha'] = alpha
        stats['beta'] = beta
        stats['xi'] = self._calcxi(observations,stats['alpha'],stats['beta'])
        stats['gamma'] = self._calcgamma(stats['xi'],len(observations))
        
        return stats
    
    def _reestimate(self,stats,observations):
        '''
        Performs the 'M' step of the Baum-Welch algorithm.
        
        Deriving classes should override (extend) this method to include
        any additional computations their model requires.
        
        Returns 'new_model', a dictionary containing the new maximized
        model's parameters.
        '''        
        new_model = {}
        
        # new init vector is set to the frequency of being in each step at t=0 
        new_model['pi'] = stats['gamma'][0]
        new_model['A'] = self._reestimateA(observations,stats['xi'],stats['gamma'])
        
        return new_model
    
    def _baumwelch(self,observations):
        '''
        An EM(expectation-modification) algorithm devised by Baum-Welch. Finds a local maximum
        that outputs the model that produces the highest probability, given a set of observations.
        
        Returns the new maximized model parameters
        '''        
        # E step - calculate statistics
        stats = self._calcstats(observations)
        
        # M step
        return self._reestimate(stats,observations)

    def _mapB(self,observations):
        '''
        Deriving classes should implement this method, so that it maps the observations'
        mass/density Bj(Ot) to Bj(t).
        
        This method has no explicit return value, but it expects that 'self.B_map' is internally computed
        as mentioned above. 'self.B_map' is an (TxN) numpy array.
        
        The purpose of this method is to create a common parameter that will conform both to the discrete
        case where PMFs are used, and the continuous case where PDFs are used.
        
        For the continuous case, since PDFs of vectors could be computationally 
        expensive (Matrix multiplications), this method also serves as a caching mechanism to significantly
        increase performance.
        '''
        raise NotImplementedError("a mapping function for B(observable probabilities) must be implemented")
        
