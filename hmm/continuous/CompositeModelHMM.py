#!/usr/bin/python
'''

@author: Benjo
'''

from hmm._BaseHMM import _BaseHMM
import numpy
import numpy.linalg
import scipy.stats

k_min_poisson_mean = 0.01


def model_factory(model_type, model_data, obsnum):
    
    if model_type == 'uniform':
        print 'creating uniform model'
        return UniformModel(obsnum, model_data);
    elif model_type == 'poisson':
        print 'creating poisson model'
        return PoissonModel(obsnum, model_data)
        
    return None

class PoissonModel(object):
    def __init__(self, obsnum, data):
        self.obsnum = obsnum
        self.dist = scipy.stats.poisson(data)
        self.mean = data
        

    def eval(self, x):
        data = numpy.round(x[:, self.obsnum]).astype(int)
        the_eval = self.dist.pmf(data)
        return the_eval
        
    def reestimate(self, x, gammaForThisState):
        '''
        Helper method that performs the Baum-Welch 'M' step
        for the mixture parameters - 'w', 'means', 'covars'.
        '''       
        newmean = 0.0
        
        numer = 0.0
        denom = 0.0
        for t in xrange(x.shape[0]):
            myobs = x[t][self.obsnum]
            
            numer += (gammaForThisState[t]*myobs)
            denom += (gammaForThisState[t])
    
        newmeans = numer/denom
    
        if newmeans < k_min_poisson_mean:
            newmeans = k_min_poisson_mean;
                
        self.mean = newmeans
        self.dist = scipy.stats.poisson(self.mean)

        
    def to_dict(self):
        return {'model_type' : 'poisson', 'model_data' : self.mean}
        
        
class UniformModel(object):
    def __init__(self, obsnum, data):
        self.obsnum = obsnum
        self.mean = data
        
    def eval(self, x):
        return self.mean
        
    
    def reestimate(self, x, gammaForThisState):
       foo =3 # do nothing!
       
    def to_dict(self):
        return {'model_type' : 'uniform', 'model_data' : self.mean}
       
class CompositeModel(object):
    def __init__(self):
        self.models = []
        
    def add_model(self, model_type, model_data, obsnum):
        model = model_factory(model_type, model_data, obsnum)
        
        if model is not None:
            self.models.append(model)
            
    def add_model_from_dict(self, model_dict, obsnum):
        model_type = model_dict['model_type']
        model_data = model_dict['model_data']
            
        self.add_model(model_type, model_data, obsnum)
        
        
            
    def eval(self, x):
        liks = numpy.ones((x.shape[0],))
        
        for model in self.models:
            liks2 = model.eval(x)
            liks = liks * liks2
        
        return liks
        
    def reestimate(self, x, gammaForThisState):
        for i in range(len(self.models)):
            self.models[i].reestimate(x, gammaForThisState)
            
    def to_dict(self):
        my_dicts = []
        for model in self.models:
            my_dicts.append(model.to_dict())
            
        return my_dicts
    

class CompositeModelHMM(_BaseHMM):

    def __init__(self,model_list = [], A=None,pi=None,precision=numpy.double,verbose=False):
        '''
        "Comments are for the weak" -- benjo
        
        '''
        
        n = len(model_list)

        if len(model_list) == 0:
            n = None
        
        
        _BaseHMM.__init__(self,len(model_list),0,precision,verbose) 
        
        self.A = A
        self.pi = pi
        self.n = n
        
        self._initModels(model_list)

    def _initModels(self, model_list):
        self.models = []
        if self.n is not None:

            for i in xrange(self.n):
                self.models.append(CompositeModel()) 
        
            for i in xrange(self.n):
                models_for_this_state = model_list[i]
                print models_for_this_state
                for j in xrange(len(models_for_this_state)):
                    self.models[i].add_model_from_dict(models_for_this_state[j], j)
    
    def _mapB(self,observations):
        self.B_map = numpy.zeros( (self.n,observations.shape[0]), dtype=self.precision)
        for i in xrange(self.n):
            self.B_map[i, :] = self.models[i].eval(observations)
        
       
                
            
    def _reestimate(self,stats,observations):
        #get A and pi
        new_model = _BaseHMM._reestimate(self, stats, observations)
        
        gamma = stats['gamma']
        for i in xrange(len(self.models)):
            self.models[i].reestimate(observations, gamma[:, i])
    
        
        return new_model
    

    
    
    def to_dict(self):
        model_list = []
        for model in self.models:
            model_list.append(model.to_dict())
        
        mydict = {}
        mydict['type'] = 'composite'
        mydict['A'] = self.A.tolist()
        mydict['pi'] = self.pi.tolist()
        mydict['models'] = model_list
        
        return mydict
        
    def from_dict(self, mydict):
        self.A = numpy.array(mydict['A'])
        self.pi = numpy.array(mydict['pi'])
        self.n = self.A.shape[0]
        self._initModels(mydict['models'])

    

def test():
    numpy.set_printoptions(precision=3, suppress=True, threshold=numpy.nan)
    #n=None,model_list = [], A=None,pi=None,thetas=None, precision
    print 'testing composite model'
    A = numpy.array([[0.9, 0.1], 
                     [0.1, 0.9]])
                
                
    pi = [0.95, 0.05]
    
    model1 = [{'model_type' : 'poisson' ,  'model_data' : 1.0}]
    model2 = [{'model_type' : 'poisson' ,  'model_data' : 5.0}]

    models = [model1, model2]
    
    
    a = CompositeModelHMM(models, A, pi)
    
    obs = numpy.array([ [1.0], [1.0], [1.0], [6.0], [6.0], [6.0], [1.0], [6.0], [1.0], [1.0]])
    
    a.train(obs, 20)
    
    for model in a.models:
        for m2 in model.models:
            print m2.mean
            
    print a.A
    
    print a.to_dict()
    
    my_dict = a.to_dict()
    
    b = CompositeModelHMM()
    b.from_dict(my_dict)
    
    print b.to_dict()
    
    b.train(obs, 1)
    
    for model in b.models:
        for m2 in model.models:
            print m2.mean
            
    print b.A


  
    
    
    
    
if __name__ == '__main__':
    test()
