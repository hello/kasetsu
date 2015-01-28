#!/usr/bin/python
'''

@author: Benjo
'''

from hmm._BaseHMM import _BaseHMM
import numpy
import numpy.linalg
import scipy.stats

k_min_variance = 1e-4

class PoissonHMM(_BaseHMM):
    '''
    HMM for the continuous likelihood function
    
    L(theta,x) = exp(theta'*x - 0.5*theta'*theta)
    d log(L) / dtheta = x - theta
    
    x is a normalized unit vector of d dimensions
    
    Model attributes:
    - n            number of hidden states
    - A            hidden states transition probability matrix ([NxN] numpy array)
    - pi           initial state's PMF ([N] numpy array).
    - theta        model parameters (MEAN)
    - w            model absolute weights
    - d            number independent models (obs vector is d x 1 per time instant)
    
    thetas is a list of lists (or a list of tuples)
    theta[0][0] == normalized vector of obs
    theta[0][1] == angular variance of obs
    
    '''

    def __init__(self,n=None, d = 1, A=None,pi=None,thetas=None, precision=numpy.double,verbose=False):
        '''
        Construct a new Continuous HMM.
        In order to initialize the model with custom parameters,
        pass values for (A,means,covars,w,pi), and set the init_type to 'user'.
        
        Normal initialization uses a uniform distribution for all probablities,
        and is not recommended.
        
        
        '''
        _BaseHMM.__init__(self,n,0,precision,verbose) #@UndefinedVariable
        
        self.A = A
        self.pi = pi
        self.thetas = numpy.array(thetas)
        self.d = d

    
    def _mapB(self,observations):
        '''
        Required implementation for _mapB. Refer to _BaseHMM for more details.
        Implements the pdf, too.
        
        '''    

        self.B_map = numpy.zeros( (self.n,len(observations)), dtype=self.precision)
        for t in xrange(len(observations)):

            for j in xrange(self.n):
                myobs = observations[t]
                joint = 1.0

                for d in xrange(self.d):
                    mean = self.thetas[d][j]
                    eval = scipy.stats.poisson.pmf(myobs[d], mean)
                    #if eval < 1e-6:
                    #    print eval, mean, myobs[d]
                        
                    joint *= eval
               
                self.B_map[j][t] = joint
                
                
            
    def _updatemodel(self,new_model):
        '''
        Required extension of _updatemodel. Adds 'w', 'means', 'covars',
        which holds the in-state information. Specfically, the parameters
        of the different mixtures.
        '''        
        _BaseHMM._updatemodel(self,new_model) #@UndefinedVariable
        
        self.thetas = new_model['thetas']
        
    
    def _reestimate(self,stats,observations):
        #get A and pi
        new_model = _BaseHMM._reestimate(self, stats, observations)
        
        new_model['thetas'] = self._reestimateTheta(observations, stats['gamma'])
        
        return new_model
    
    def _reestimateTheta(self,observations,gamma):
        '''
        Helper method that performs the Baum-Welch 'M' step
        for the mixture parameters - 'w', 'means', 'covars'.
        '''        
        newmeans = numpy.zeros( (self.d, self.n), dtype=self.precision)
    
        for j in xrange(self.n):
            for d in xrange(self.d):
                numer = numpy.zeros( 1, dtype=self.precision)
                denom = numpy.zeros( 1, dtype=self.precision)
                for t in xrange(len(observations)):
                    myobs = observations[t][d]
                    numer += (gamma[t][j]*myobs)
                    denom += (gamma[t][j])
            
                newmeans[d][j] = numer/denom
        
        print newmeans
        return newmeans
    

    def to_dict(self):
        mydict = {}
        mydict['type'] = 'PoissonHMM'
        mydict['A'] = self.A.tolist()
        mydict['pi'] = self.pi.tolist()
        mydict['means'] = self.thetas.tolist()
        mydict['nummodels'] = self.d
        
        return mydict
        
    def from_dict(self, mydict):
        self.A = numpy.array(mydict['A'])
        self.pi = numpy.array(mydict['pi'])
        self.thetas = numpy.array(mydict['means'])
        self.n = self.A.shape[0]
        self.d = mydict['nummodels']

    
