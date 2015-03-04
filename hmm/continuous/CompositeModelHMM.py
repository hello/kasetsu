#!/usr/bin/python
'''

@author: Benjo
'''

from hmm._BaseHMM import _BaseHMM
import numpy
import numpy.linalg
import scipy.stats
import copy
import numpy.random


k_min_poisson_mean = 0.01
k_min_gaussian_variance = 0.01
k_max_gaussian_variance = 100

k_min_gamma_mean = 0.01
k_min_gamma_variance = 0.01


def model_factory(model_type, model_data):
    
    if model_type == 'uniform':
        print 'creating uniform model'
        return UniformModel(model_data)
        
    elif model_type == 'poisson':
        print 'creating poisson model'
        return PoissonModel(model_data)
        
    elif model_type == 'gaussian_mixture':
        return OneDimensionalGaussianMixture(model_data)
        
    elif model_type == 'gamma':
        return GammaDistribution(model_data)
        
    elif model_type == 'discrete_alphabet':
        print 'creating discrete model'
        return DiscreteAlphabetModel(model_data)
        
    return None

class PoissonModel(object):
    def __init__(self, data):
        self.obsnum = data['obs_num']
        self.mean = data['mean']
        self.dist = scipy.stats.poisson(self.mean)
    
    def eval(self, x):
        data = numpy.round(x[:, self.obsnum]).astype(int)
        the_eval = self.dist.pmf(data)
        return the_eval
        
    def reestimate(self, x, gammaForThisState):
        
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
        
    def get_status(self):
        return "psn %.2f" % (self.mean)

        
    def to_dict(self):
        return {'model_type' : 'poisson', 'model_data' : {'mean' : self.mean,  'obs_num' : self.obsnum} }
        

class GammaDistribution(object):
    def __init__(self, data):
        self.obsnum = data['obs_num']
        self.mean  = data['mean']
        self.stddev = data['stddev']
        self.dist = self.get_dist()
        
        
    def get_dist(self):
        variance = self.stddev*self.stddev
        theta = variance / self.mean
        k = self.mean / theta
        #print k, theta
        return scipy.stats.gamma(k, scale=theta)
        
    def get_params(self):
        theta = self.dist.var() / self.dist.mean()
        k = self.dist.mean() / theta
        return (k, theta)
        
    def eval(self, x):
        data = x[:, self.obsnum]
                
        the_eval = self.dist.pdf(data)

        #print data[30:40]
        #print the_eval[30:40]
        #print self.dist
        #print self.get_params()
        return the_eval
        
        
    def reestimate(self, x, gammaForThisState):
        
        oldmean = self.mean
        
        newmean = 0.0
        
        numer_mean = 0.0
        numer_variance = 0.0
        denom = 0.0
        for t in xrange(x.shape[0]):
            myobs = x[t][self.obsnum]
            dx = myobs - oldmean

            numer_mean += gammaForThisState[t]*myobs
            numer_variance += gammaForThisState[t]*dx*dx
            denom += (gammaForThisState[t])
    
        newmean = numer_mean/denom
        newvariance = numer_variance / denom
    
        if newmean < k_min_gamma_mean:
            newmean = k_min_gamma_mean
            
        if newvariance < k_min_gamma_variance:
            newvariance = k_min_gamma_variance
            
        self.mean = newmean 
        self.stddev = numpy.sqrt(newvariance)
        
        
    def to_dict(self):
        return {'model_type' : 'gamma', 'model_data' : {'mean' : self.mean, 'stddev' : self.stddev,   'obs_num' : self.obsnum} }


    def get_status(self):
        return "m=%.2f,s=%.2f" % (self.mean, self.stddev)


class OneDimensionalGaussianMixture(object):
    def __init__(self, data):
        self.obsnum = data['obs_num']
        self.data = data
        
    def eval_gaussian(self, mean, variance, x):
        dx = x - mean
        y = numpy.exp( -(dx*dx) / (2*variance))
        y[numpy.where(y <= 1e-5)] = 1e-5
        y /= numpy.sqrt(2*3.14159*variance)
        return y

    def eval(self, x):
        weights = self.data['weights']
        means = self.data['means']
        variances = self.data['variances']
        
        n = len(weights)
        
        measvec = x[:, self.obsnum]
        
        evals = numpy.ones(measvec.shape)
        for i in xrange(n):
            y = weights[i] * self.eval_gaussian(means[i], variances[i], measvec)
            evals *= y
        
        return evals
        
    def reestimate(self, x, gammaForThisState):
        '''
        Helper method that performs the Baum-Welch 'M' step
        for the mixture parameters - 'w', 'means', 'covars'.
        '''       
        
        weights = self.data['weights']
        means = self.data['means']
        variances = self.data['variances']
        
        n = len(weights)
        
        newweights = copy.deepcopy(weights)
        newmeans = copy.deepcopy(means)
        newvariances = copy.deepcopy(variances)
        
        measvec = x[:, self.obsnum]
        m = measvec.shape[0]
        
        total_denom = sum(gammaForThisState)
            
        
        for i in xrange(n):
            
            mydenomsum = 0.0
            mycovsum   = 0.0
            mymeansum  = 0.0
            
            for t in xrange(m):
                mymeansum += gammaForThisState[t] * measvec[t]
                dx = measvec[t] - means[i]
                mycovsum += gammaForThisState[t] * dx*dx
                mydenomsum += gammaForThisState[t]
                
                
            newweights[i] = mydenomsum / total_denom
            newvariances[i] = mycovsum / mydenomsum
            newmeans[i] = mymeansum / mydenomsum

            if newvariances[i] < k_min_gaussian_variance:
                newvariances[i] = k_min_gaussian_variance
                
            if newvariances[i] > k_max_gaussian_variance:
                newvariances[i] = k_max_gaussian_variance

            
        
        self.means = newmeans
        self.weights = newweights
        self.variances = newvariances
        
    def get_status(self):
        return "m=%.2f,s=%.2f,w=%f" % (self.means[0], numpy.sqrt(self.variances[0]), self.weights[0])

        
    def to_dict(self):
        return {'model_type' : 'gaussian_mixture', 'model_data' : {'mean' : self.mean,  'obs_num' : self.obsnum}}
        
        
class UniformModel(object):
    def __init__(self, data):
        self.obsnum = data['obs_num']
        self.mean = data['mean']
        
    def eval(self, x):
        return self.mean
        
    
    def reestimate(self, x, gammaForThisState):
       foo =3 # do nothing!
       
       
    def get_status(self):
        return "uni {:<10.2f}".format(self.mean)

    def to_dict(self):
        return {'model_type' : 'uniform', 'model_data' : self.mean,  'obs_num' : self.obsnum}
      
    
class DiscreteAlphabetModel(object):
    def __init__(self, data):
        self.obsnum = data['obs_num']
        self.data = data['alphabet_probs']
                
    def eval(self, x):
        xvec = x[:, self.obsnum].astype(int)
        
        ret = numpy.zeros(xvec.shape)
        xvec = xvec.tolist()
        for i in xrange(len(xvec)):
            ret[i] = self.data[xvec[i]]
        
        return ret
        
    
    def reestimate(self, x, gammaForThisState):
        num_obs = x.shape[0]
        m = len(self.data)
        xvec = x[:, self.obsnum].tolist()
        
        denom = numpy.sum(gammaForThisState)
        Bnew = copy.deepcopy(self.data)
        for k in xrange(m):
            numer = 0.0
            
            for t in xrange(num_obs):
                if xvec[t] == k:
                    numer += gammaForThisState[t]
                
            Bnew[k] = numer/denom    
         
        self.data = Bnew
       
    def get_status(self):
        return ",".join([("%.2f" % f) for f in self.data])

    def to_dict(self):
        return {'model_type' : 'discrete_alphabet', 'model_data' : { 'alphabet_probs' : self.data,  'obs_num' : self.obsnum} }
        
        
class CompositeModel(object):
    def __init__(self):
        self.models = []
        
    def add_model(self, model_type, model_data):
        model = model_factory(model_type, model_data)
        
        if model is not None:
            self.models.append(model)
            
    def add_model_from_dict(self, model_dict):
        model_type = model_dict['model_type']
        model_data = model_dict['model_data']
            
        self.add_model(model_type, model_data)
        
        
            
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
        
    def get_status(self):
        status_line  = []
        for model in self.models:
            status_line.append(model.get_status())
            
        return ",".join(status_line)

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
                    self.models[i].add_model_from_dict(models_for_this_state[j])
    
    def _mapB(self,observations):
        self.B_map = numpy.zeros( (self.n,observations.shape[0]), dtype=self.precision)
        for i in xrange(self.n):
            self.B_map[i, :] = self.models[i].eval(observations)
        
       
                
    def get_status(self):
        for i in xrange(len(self.models)):
            print "model %d: %s" % (i, self.models[i].get_status())
            
    def _reestimate(self,stats,observations):
        #get A and pi
        new_model = _BaseHMM._reestimate(self, stats, observations)
        
        gamma = stats['gamma']
        for i in xrange(len(self.models)):
            self.models[i].reestimate(observations, gamma[:, i])
    
        self.get_status()

        
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
    
    print a.means
    print a.variances
    print a.weights
            
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


  
    
def test_gaussian():
    numpy.set_printoptions(precision=3, suppress=True, threshold=numpy.nan)
    print 'testing composite model'
    A = numpy.array([[0.9, 0.1], 
                     [0.1, 0.9]])
                
                
    pi = [0.95, 0.05]
    
    model1 = [{'model_type' : 'gaussian' ,  'model_data' : {'means' : [2.0], 'variances' : [1.0],  'weights' : [1.0] }}]
    model2 = [{'model_type' : 'gaussian' ,  'model_data' : {'means' : [8.0], 'variances' : [4.0],  'weights' : [1.0] }}]

    models = [model1, model2]
    
    
    a = CompositeModelHMM(models, A, pi)
    obs = numpy.concatenate( (0.5*numpy.random.randn(200, 1), 0.2*numpy.random.randn(200, 1) + 10), axis=0)
        
    a.train(obs, 10)

    print a.A
    
def gen_model(p, n):
    p2 = numpy.cumsum(numpy.array(p))
    
    ret = []
    for i in xrange(n):
        peval = numpy.random.rand()
        for j in xrange(len(p2)):
            if peval > p2[j]:
                break;
                
        ret.append(j)
            
    return ret
    
def test_discrete():
    A = numpy.array([[0.9, 0.1], 
                     [0.1, 0.9]])
                     
    model1 = [{'model_type' : 'discrete_alphabet' ,  'model_data' : [0.8, 0.2]}]
    model2 = [{'model_type' : 'discrete_alphabet' ,  'model_data' : [0.2, 0.8]}]

    p1 = [0.1, 0.9]
    p2 = [0.5, 0.5]
    
    v = []
    for i in xrange(20):
        v1 = gen_model(p1, 25)
        v2 = gen_model(p2, 25)
        v.extend(v1)
        v.extend(v2)
        
   
    v = numpy.array(v).reshape(len(v), 1)
 
    models = [model1, model2]
    
    pi = [0.95, 0.05]

    a = CompositeModelHMM(models, A, pi)
    
    a.train(v, 20)
    
    print a.A
    

    
    

    
    

