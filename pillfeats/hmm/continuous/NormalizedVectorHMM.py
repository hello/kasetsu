#!/usr/bin/python
'''

@author: Benjo
'''

from hmm._BaseHMM import _BaseHMM
import numpy
import numpy.linalg

class NormalizedVectorHMM(_BaseHMM):
    '''
    HMM for the continuous likelihood function
    
    L(theta,x) = exp(theta'*x - 0.5*theta'*theta)
    d log(L) / dtheta = x - theta
    
    x is a normalized unit vector of d dimensions
    
    Model attributes:
    - n            number of hidden states
    - d            number of features (an observation can contain multiple features)
    - A            hidden states transition probability matrix ([NxN] numpy array)
    - pi           initial state's PMF ([N] numpy array).
    - theta        model parameters
    
  
    '''

    def __init__(self,n,d,A,pi,thetas, precision=numpy.double,verbose=False):
        '''
        Construct a new Continuous HMM.
        In order to initialize the model with custom parameters,
        pass values for (A,means,covars,w,pi), and set the init_type to 'user'.
        
        Normal initialization uses a uniform distribution for all probablities,
        and is not recommended.
        '''
        _BaseHMM.__init__(self,n,0,precision,verbose) #@UndefinedVariable
        
        self.d = d
        self.A = A
        self.pi = pi
        self.thetas = thetas

    
    def _mapB(self,observations):
        '''
        Required implementation for _mapB. Refer to _BaseHMM for more details.
        Implements the pdf, too.
        
        '''    
        thetasq = []
        for j in xrange(self.n):
            thetasq.append(numpy.sum(self.thetas[j]*self.thetas[j]))
            
        self.B_map = numpy.zeros( (self.n,len(observations)), dtype=self.precision)
        for j in xrange(self.n):
            for t in xrange(len(observations)):
                cos = numpy.sum(self.thetas[j] * observations[t])
                sin = numpy.sqrt(1 - cos*cos)
                tan_over_2 = sin/(numpy.abs((1 + cos)) + 1e-6)
                self.B_map[j][t] = numpy.exp(-tan_over_2*tan_over_2*50)
                
        #print self.B_map
                
            
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
        theta = numpy.zeros( (self.n,self.d), dtype=self.precision)
    
        for j in xrange(self.n):
            numer = numpy.zeros( (self.d), dtype=self.precision)
            denom = numpy.zeros( (self.d), dtype=self.precision)
            for t in xrange(len(observations)):
                #print gamma[t][j], observations[t]
                numer += (gamma[t][j]*observations[t])
                denom += (gamma[t][j])
            theta[j] = numer/denom
            
            #print j, numer, denom
            theta[j] = theta[j] / numpy.linalg.norm(theta[j])
                
        return theta
    

    
    
