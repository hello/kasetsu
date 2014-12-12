#!/usr/bin/python

from hmm.discrete.DiscreteHMM import DiscreteHMM
import numpy
'''
Handles the case of multiple training sets 
and multiple independnet observation types
'''

k_min_loglik = -100

class MultipleDiscreteHMM(object):
    def __init__(self,A,pi,precision=numpy.double,verbose=False):
        self.obsmodels = []

        self.A = A
        self.pi = pi
        
        self.precision = numpy.double
        self.verbose = verbose
        self.n = A.shape[0] #be square
        
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
    '''
    observations should be a list of vector observations
     obs[model][list of observations]
     
     
    '''
    def training_iter(self, observations):
        model_loglik = []
        numerAlist = []
        denomAlist = []
        

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
            
            params = []
            logliks = []
            
            #evaluate, collect stats for this model
            for obs in observations:
                obsvec = obs[imodel][:]
                
                hmm.forwardbackward(obsvec)
                stats = hmm._calcstats(obsvec)
                
                ll = stats['loglik']
                
                if ll < k_min_loglik:
                    ll = k_min_loglik
                    
                    
                #save for later use in scaling
                logliks.append(ll)
                
                #these values come out "normalized" by likelihood
                params.append(self.compute_reestimation_params(M, stats['xi'], stats['gamma'], obsvec))
                
            logliks = numpy.array(logliks) 
            
            loglik = numpy.sum(logliks)

            medlik = numpy.median(logliks)
            logliks = logliks - medlik
            
            
            
            for i in xrange(len(observations)):
                myliklihood = numpy.exp(logliks[i])
                
                numerA2, numerB2, denomA2, denomB2 = params[i]
                
                
                numerA += numerA2/myliklihood
                numerB += numerB2/myliklihood
                denomA += denomA2/myliklihood
                denomB += denomB2/myliklihood
                

            
            #compute B update
            newB = numpy.zeros(B.shape)
            for j in xrange(B.shape[0]):
                for k in xrange(B.shape[1]):
                    newB[j][k] = numerB[j][k] / denomB[j]
                    
            
            self.obsmodels[imodel] = newB
            
            model_loglik.append(loglik)
            numerAlist.append(numerA)
            denomAlist.append(denomA)
                
            
           
        model_loglik = numpy.array(model_loglik)
        loglik_for_everything = numpy.sum(model_loglik)
        
        themax = numpy.amax(model_loglik)
        model_loglik = model_loglik[:] - themax
        weights = numpy.exp(-model_loglik)
        weights = weights / numpy.sum(weights)
        
        newA = numpy.zeros(self.A.shape)
        #compute cominated A update
        for k in range(len(model_loglik)):
            lik = numpy.exp(model_loglik[k])
        
            for j in xrange(newA.shape[0]):
                for i in xrange(newA.shape[1]):
                    newA[j][i] = newA[j][i] + weights[k]*(numerA[j][i] / denomA[j])
            
        self.A = newA
        
        return loglik_for_everything
        
    def compute_reestimation_params(self,M,  xi, gamma, obs):
        denomA = numpy.zeros((self.n, ))
        denomB = numpy.zeros((self.n, ))
        
        numerA = numpy.zeros((self.n, self.n))
        numerB = numpy.zeros((self.n, M))

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
                
                
        return (numerA, numerB, denomA, denomB)
        
  
