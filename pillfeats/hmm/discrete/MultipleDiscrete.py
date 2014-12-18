#!/usr/bin/python

from hmm.discrete.DiscreteHMM import DiscreteHMM
import numpy
from hmm._BaseHMM import _BaseHMM
import json

'''
Handles the case of multiple training sets 
and multiple independnet observation types
'''

k_min_loglik = -5

class MultipleDiscreteHMM(_BaseHMM):
    def __init__(self,A = None,pi = None,precision=numpy.double,verbose=False):
        if not A is None:
            self.obsmodels = []
    
            self.A = A
            self.pi = pi
            
            self.precision = numpy.double
            self.verbose = verbose
            self.n = A.shape[0] #be square
        
    def force_no_zero_values(self, min_val=1e-6):
        for B in self.obsmodels:
            for j in range(B.shape[0]):
                for i in range(B.shape[1]):
                    if B[j, i] < min_val:
                        B[j, i] = min_val;
         
        A = self.A
        for j in range(A.shape[0]):
            for i in range(A.shape[1]):
                if A[j, i] < min_val:
                    A[j, i] = min_val
                    
                    
            
        
    def _mapB(self,observations):
        numobs = len(observations[0])
        
        self.B_map = numpy.ones( (self.n,numobs), dtype=self.precision)
        
        for istate in xrange(self.n):
            for t in xrange(numobs):
                for imodel in xrange(len(self.obsmodels)):
                    this_obs = observations[imodel][t]
                    self.B_map[istate][t] = self.B_map[istate][t] * self.obsmodels[imodel][istate][this_obs]
                             

    def printme(self):
        print self.A
        for model in self.obsmodels:
            print model
        
        print self.pi
        
    def decode(self, observations):
        '''
        Find the best state sequence (path), given the model and an observation. i.e: max(P(Q|O,model)).
        
        This method is usually used to predict the next state after training. 
        '''        
        # use Viterbi's algorithm. It is possible to add additional algorithms in the future.
        return self._viterbi(observations, len(observations[0]))
        
    def save_to_file(self, filename):
        result = {}
        result['A'] = self.A.tolist()
        result['obsmodels'] = []
        for model in self.obsmodels:
            result['obsmodels'].append(model.tolist())
            
        result['pi'] = self.pi.tolist()
    
        f = open(filename, 'w')
        json.dump(result, f)
        f.close()
        
    def load_from_file(self, filename):
        f = open(filename, 'r')
        hmmdata = json.load(f)
        f.close()
        
        self.__init__(numpy.array(hmmdata['A']),numpy.array(hmmdata['pi']))
        
        for B in hmmdata['obsmodels']:
            B = numpy.array(B)
            self.addModel(B)
        
        
    def reset(self):
        self.obsmodels = []

    def addModel(self, B):
        self.obsmodels.append(B)
        
    def forwardbackward(self,observations,cache=False):
        total_loglik = 0.0
       
        
        for imodel in range(len(self.obsmodels)):
            B = self.obsmodels[imodel]
            M = B.shape[1]
            
            #create HMM with model parameters
            hmm = DiscreteHMM(self.n, M, self.A, B, self.pi, init_type='user', precision=self.precision, verbose=self.verbose)
            
            for obs in observations:
                obsvec = obs[imodel][:]
                
                total_loglik += hmm.forwardbackward(obsvec)
                
                
        return total_loglik
        
    def train(self, observations, numiters):
        ll2 = self.forwardbackward(observations)
        print ll2
  
        for i in range(numiters):
            print ('iter %d' % i)
            self.training_iter(observations)
            ll2 = self.forwardbackward(observations)
            print ll2
        
    '''
    observations should be a list of vector observations
     obs[model][list of observations]
     
     
    '''
    def training_iter(self, observations):
        model_loglik = []
        numerAlist = []
        denomAlist = []
        pi0list = []

        for imodel in range(len(self.obsmodels)):
            B = self.obsmodels[imodel]
            M = B.shape[1]
            
            #create HMM with model parameters
            hmm = DiscreteHMM(self.n, M, self.A, B, self.pi, init_type='user', precision=self.precision, verbose=self.verbose)
            
            loglik = 0.0

            denomA = numpy.zeros((self.n, ))
            denomB = numpy.zeros((self.n, ))
        
            numerA = numpy.zeros((self.n, self.n))
            numerB = numpy.zeros((self.n, M))
            
            pi0 = numpy.zeros((self.n, ))
            
            params = []
            logliks = []
            
            #evaluate, collect stats for this model
            for obs in observations:
                obsvec = obs[imodel][:]
                
                hmm.forwardbackward(obsvec)
                stats = hmm._calcstats(obsvec)
                
                ll = stats['loglik']
                
        
                #save for later use in scaling
                logliks.append(ll)
                
                #these values come out "normalized" by likelihood
                params.append(self.compute_reestimation_params(M, stats['xi'], stats['gamma'], obsvec))
                
            logliks = numpy.array(logliks) 
            
            loglik = numpy.sum(logliks)

            maxlik = numpy.amax(logliks)
            logliks = logliks - maxlik
            
            for i in xrange(len(logliks)):
                if logliks[i] < k_min_loglik:
                    logliks[i] = k_min_loglik
            
            
            for i in xrange(len(observations)):
                myliklihood = numpy.exp(logliks[i])
                
                numerA2, numerB2, denomA2, denomB2, gamma0 = params[i]
                
                
                numerA += numerA2/myliklihood
                numerB += numerB2/myliklihood
                denomA += denomA2/myliklihood
                denomB += denomB2/myliklihood
                pi0 += gamma0 / myliklihood
                

            
            #compute B update
            newB = numpy.zeros(B.shape)
            for j in xrange(B.shape[0]):
                for k in xrange(B.shape[1]):
                    newB[j][k] = numerB[j][k] / denomB[j]
                    
            
            self.obsmodels[imodel] = newB
            
            model_loglik.append(loglik)
            numerAlist.append(numerA)
            denomAlist.append(denomA)
            pi0list.append(pi0)
                
            

        model_loglik = numpy.array(model_loglik)
        loglik_for_everything = numpy.sum(model_loglik)
        
        themax = numpy.amax(model_loglik)
        model_loglik = model_loglik - themax

        for i in range(len(model_loglik)):
            if model_loglik[i] < k_min_loglik:
                model_loglik[i] = k_min_loglik
        
        #weights = numpy.exp(-model_loglik)
        #weights = weights / numpy.sum(weights)
        M = len(self.obsmodels)
        weights = numpy.ones((M, )) / M
                        
        newA = numpy.zeros(self.A.shape)
        newPi0 = numpy.zeros((self.n, ))
        #compute cominated A update
        for k in range(len(model_loglik)):
            lik = numpy.exp(model_loglik[k])
        
            for j in xrange(newA.shape[0]):
                for i in xrange(newA.shape[1]):
                    newA[j][i] = newA[j][i] + weights[k]*(numerA[j][i] / denomA[j])
                    
            newPi0 = newPi0 + pi0list[k]*weights[k]
            
        self.A = newA
        
        newPi0 = newPi0 / numpy.sum(newPi0)
        
        self.pi = newPi0
        
        return loglik_for_everything
        
    def compute_reestimation_params(self,M,  xi, gamma, obs):
        denomA = numpy.zeros((self.n, ))
        denomB = numpy.zeros((self.n, ))
        
        numerA = numpy.zeros((self.n, self.n))
        numerB = numpy.zeros((self.n, M))
        
        gamma0 = gamma[0]

        for i in xrange(self.n): 
            for t in xrange(len(obs)-1):
                denomA[i] += gamma[t][i]
                
            denomB[i] = denomA[i] + gamma[len(obs)-1][i]


        for i in xrange(self.n): 
            for j in xrange(self.n):
                numer = 0
                for t in xrange(len(obs)-1):
                    numer += xi[t][i][j]
                    
                numerA[i][j] = numer
                
        for j in xrange(self.n):
            for k in xrange(M):
                numer = 0.0
                
                for t in xrange(len(obs)):
                    if obs[t] == k:
                        numer += gamma[t][j]
                        
                numerB[j][k] = numer
                
                
        return (numerA, numerB, denomA, denomB, gamma0)
        
  
