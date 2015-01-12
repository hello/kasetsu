#!/usr/bin/python
'''

@author: Benjo
'''

from hmm._BaseHMM import _BaseHMM
import numpy
import numpy.linalg

k_min_variance = 1e-4

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
    
    thetas is a list of lists (or a list of tuples)
    theta[0][0] == normalized vector of obs
    theta[0][1] == angular variance of obs
    
    '''

    def __init__(self,n=None,d=None,A=None,pi=None,thetas=None,precision=numpy.double,verbose=False):
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

        self.B_map = numpy.zeros( (self.n,len(observations)), dtype=self.precision)
        for j in xrange(self.n):
            for t in xrange(len(observations)):
                vec = self.thetas[j][0]
                variance = self.thetas[j][1]
                myobs = observations[t]
                myobs = myobs / numpy.linalg.norm(observations[t])
                dotprod = numpy.sum(vec * myobs)
                tan_over_2_sq = (1.0 - dotprod) / ( (1.0 + dotprod) + 1e-6 )
                arg = -tan_over_2_sq / variance
                #print arg,dotprod, tan_over_2_sq,  variance
                self.B_map[j][t] = numpy.exp(arg)
                
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
        vecs = numpy.zeros( (self.n,self.d), dtype=self.precision)
    
        for j in xrange(self.n):
            numer = numpy.zeros( (self.d), dtype=self.precision)
            denom = numpy.zeros( (self.d), dtype=self.precision)
            for t in xrange(len(observations)):
                myobs = observations[t]
                myobs = myobs / numpy.linalg.norm(observations[t])
                numer += (gamma[t][j]*myobs)
                denom += (gamma[t][j])
            
            vecs[j] = numer/denom
            vecs[j] = vecs[j] / numpy.linalg.norm(vecs[j])

            #print j, numer, denom
                        
        vars = numpy.zeros((self.n, ), dtype=self.precision)
        for j in xrange(self.n):
            numer = 0.0
            denom = 0.0
            for t in xrange(len(observations)):
                myobs = observations[t]
                myobs = myobs / numpy.linalg.norm(observations[t])
                
                v = self.thetas[j][0]
                dotprod = numpy.sum(v * myobs)
                tan_over_2_sq = (1.0 - dotprod) / ((1.0 + dotprod) + 1e-6)
                var = 2.0*tan_over_2_sq
                numer += (gamma[t][j]*var)
                denom += (gamma[t][j])
                
            vars[j] = numer/denom
            
            vars[j] = numpy.fabs(vars[j])
            
            if vars[j] < k_min_variance:
                vars[j] = k_min_variance
            
            
        
        thetas = []
        for j in xrange(self.n):
            thetas.append([vecs[j], vars[j]])
            
        return thetas
    

    def to_dict(self):
       
        
        mydict = {}
        mydict['type'] = 'NormalizedVectorHMM'
        mydict['A'] = self.A.tolist()
        mydict['pi'] = self.pi.tolist()
        mydict['vecs'] = []
        mydict['vars'] = []

        for theta in self.thetas:
            mydict['vecs'].append(theta[0].tolist())
            mydict['vars'].append(theta[1])
        

        return mydict
        
    def from_dict(self, mydict):
        self.A = numpy.array(mydict['A'])
        self.pi = numpy.array(mydict['pi'])
        self.thetas = []
        
        
        for i in xrange(len(mydict['vecs'])):
            vec = numpy.array(mydict['vecs'][i])
            var = mydict['vars'][i]
            
            self.thetas.append([vec, var])
            
            
        self.n = self.A.shape[0]
        self.d = vec.shape[0]
        

    
