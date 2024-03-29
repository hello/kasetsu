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

k_min_chisquare_input = 0.01
k_min_poisson_mean = 0.01
k_min_gaussian_variance = 0.01
k_max_gaussian_variance = 100

k_min_gamma_mean = 0.01
k_min_gamma_variance = 0.01
k_min_val_for_gamma = 0.1

k_min_loglik = -15.0

def model_factory(model_type, model_data):
    
    if model_type == 'uniform':
        return UniformModel(model_data)
        
    elif model_type == 'poisson':
        return PoissonModel(model_data)
    elif model_type == 'chisquare':
        return ChiSquareModel(model_data)
    elif model_type == 'gaussian':
        return OneDimensionalGaussian(model_data)
    elif model_type == 'multigauss':
        return MultivariateGaussian(model_data)
    elif model_type == 'beta':
        return BetaModel(model_data)
    elif model_type == 'gamma':
        return GammaDistribution(model_data)
    elif model_type == 'discrete_alphabet':
        return DiscreteAlphabetModel(model_data)
    else:
        print 'ERROR: %s unrecognized model!!!!' % model_type
        
    return None

class MultivariateGaussian(object):
    def __init__(self,data):
        self.obsnums = data['obs_nums']
        if data.has_key('weight'):
            self.weight = data['weight']
        else:
            self.weight = 1.0

        self.mean = numpy.array(data['means'])
        covvec = data['cov']
        n = len(self.mean)
        self.cov = self.vec_to_cov(covvec,n)
 

    def vec_to_cov(self,covvec,n):
        cov = numpy.zeros((n,n))
        k = 0
        for j in range(n):
            for i in range(n - j):
                ii = i + j;
                cov[j,ii] = covvec[k]
                k += 1

        return cov

    def cov_to_vec(self,cov):
        n = cov.shape[0]
        covvec = []
        k = 0
        for j in range(n):
            for i in range(n - j):
                ii = i + j;
                covvec.append(cov[j,ii])
                k += 1;

        return covvec

    def to_dict(self):
        return {'model_type' : 'beta', 'model_data' : {'means' : self.mean.tolist(), 'covs' : self.cov_to_vec(self.cov),  'obs_nums' : self.obsnums,  'weight' : self.weight } }

    def get_status(self):
        return "mgmean:%s" % (numpy.array_str(self.mean))

    def eval(self, x):
        self.dist = scipy.stats.multivariate_normal(self.mean,self.cov)                             
        data = x[:, self.obsnums]
        the_eval = self.dist.pdf(data)
        return the_eval
                
class BetaModel(object):
    def __init__(self, data):
        self.obsnum = data['obs_num']
        self.alpha = data['alpha']
        self.beta = data['beta']

        if data.has_key('weight'):
            self.weight = data['weight']
        else:
            self.weight = 1.0
            
        self.dist = scipy.stats.beta(self.alpha,self.beta)

    def eval(self, x):
        data = x[:, self.obsnum]
        the_eval = self.dist.pdf(data)
        return the_eval

    def get_status(self):
        return "beta:%.2f,%.2f" % (self.alpha,self.beta)

        
    def to_dict(self):
        return {'model_type' : 'beta', 'model_data' : {'beta' : self.beta, 'alpha' : self.alpha,  'obs_num' : self.obsnum,  'weight' : self.weight } }
    
        
class PoissonModel(object):
    def __init__(self, data):
        self.obsnum = data['obs_num']
        self.mean = data['mean']
        
        if data.has_key('weight'):
            self.weight = data['weight']
        else:
            self.weight = 1.0
            
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
        return "psn:%.2f" % (self.mean)

        
    def to_dict(self):
        return {'model_type' : 'poisson', 'model_data' : {'mean' : self.mean,  'obs_num' : self.obsnum,  'weight' : self.weight } }
        
class ChiSquareModel(object):
    def __init__(self, data):
        self.obsnum = data['obs_num']
        self.mean = data['mean']
        
        if data.has_key('weight'):
            self.weight = data['weight']
        else:
            self.weight = 1.0
            
        self.dist = scipy.stats.chi2(self.mean)
    
    def eval(self, x):
        xc = numpy.array(copy.deepcopy(x[:, self.obsnum]))
        xc[numpy.where(xc < k_min_chisquare_input)] = k_min_chisquare_input;
        the_eval = self.dist.pdf(xc)
        return the_eval
        
 
        
    def get_status(self):
        return "chi:%.2f" % (self.mean)

        
    def to_dict(self):
        return {'model_type' : 'chisquare', 'model_data' : {'mean' : self.mean,  'obs_num' : self.obsnum,  'weight' : self.weight } }
    
class GammaDistribution(object):
    def __init__(self, data):
        self.obsnum = data['obs_num']
        self.mean  = data['mean']
        self.stddev = data['stddev']
        
        if data.has_key('weight'):
            self.weight = data['weight']
        else:
            self.weight = 1.0
            
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
               
        data[numpy.where(data < k_min_val_for_gamma)] = k_min_val_for_gamma
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
        return {'model_type' : 'gamma', 'model_data' : {'mean' : self.mean, 'stddev' : self.stddev,   'obs_num' : self.obsnum,  'weight' : self.weight } }


    def get_status(self):
        return "gam:%.2f,%.2f" % (self.mean, self.stddev)



class OneDimensionalGaussian(object):
    def __init__(self, data):
        self.obsnum = data['obs_num']
        self.mean  = data['mean']
        self.stddev = data['stddev']
        
        if data.has_key('weight'):
            self.weight = data['weight']
        else:
            self.weight = 1.0
            
        self.dist = self.get_dist()
        
        
    def get_dist(self):
 
        return scipy.stats.norm(loc=self.mean, scale=self.stddev)
        
    def get_params(self):
        return (self.dist.mean(), self.dist.std())
        
    def eval(self, x):
        data = x[:, self.obsnum]
               
        the_eval = self.dist.pdf(data)

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
        self.dist = self.get_dist()

        
        
    def to_dict(self):
        return {'model_type' : 'gaussian', 'model_data' : {'mean' : self.mean, 'stddev' : self.stddev,   'obs_num' : self.obsnum,  'weight' : self.weight } }


    def get_status(self):
        return "gaus:%.2f,%.2f" % (self.mean, self.stddev)


        
class UniformModel(object):
    def __init__(self, data):
        self.obsnum = data['obs_num']
        self.mean = data['mean']
        
        if data.has_key('weight'):
            self.weight = data['weight']
        else:
            self.weight = 1.0
        
    def eval(self, x):
        return self.mean
        
    
    def reestimate(self, x, gammaForThisState):
       foo =3 # do nothing!
       
       
    def get_status(self):
        return "uni {:<10.2f}".format(self.mean)

    def to_dict(self):
        return {'model_type' : 'uniform', 'model_data' : self.mean,  'obs_num' : self.obsnum,  'weight' : self.weight }
      
    
class DiscreteAlphabetModel(object):
    def __init__(self, data):
        self.obsnum = data['obs_num']
        self.data = data['alphabet_probs']
        
        if data.has_key('weight'):
            self.weight = data['weight']
        else:
            self.weight = 1.0
        
        if data.has_key('allow_reestimation'):
            self.allow_reestimation = data['allow_reestimation']
        else:
            self.allow_reestimation = True
        
    def eval(self, x):
        xvec = x[:, self.obsnum].astype(int)
        
        ret = numpy.zeros(xvec.shape)
        xvec = xvec.tolist()
        for i in xrange(len(xvec)):
            ret[i] = self.data[xvec[i]]
        
        return ret
        
    
    def reestimate(self, x, gammaForThisState):
        
        if not self.allow_reestimation:
            return
        
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
        return "alph:" + ",".join([("%.2f" % f) for f in self.data])

    def to_dict(self):
        return {'model_type' : 'discrete_alphabet', 'model_data' : { 'alphabet_probs' : self.data,  'obs_num' : self.obsnum, 'allow_reestimation' : self.allow_reestimation,  'weight' : self.weight } }
        
        
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
        logliks = numpy.zeros((x.shape[0],))
        
        for model in self.models:
            logliks2 = model.weight * numpy.log(model.eval(x))
            logliks += logliks2 
        
        return logliks
        
    def reestimate(self, x, gammaForThisState, reestimation_obs):
        if reestimation_obs == None:
            for i in range(len(self.models)):
                self.models[i].reestimate(x, gammaForThisState)
        else:
            for i in reestimation_obs:
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
            
        return ",  ".join(status_line)

class CompositeModelHMM(_BaseHMM):

    def __init__(self,model_list = [], A=None,pi=None, precision=numpy.double,verbose=False):
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
        self.reestimation_obs = None
        
        self._initModels(model_list)

    def set_reestimation_obs(self, reestimation_obs):
        self.reestimation_obs = reestimation_obs
        
    def _initModels(self, model_list):
        self.models = []
        if self.n is not None:

            for i in xrange(self.n):
                self.models.append(CompositeModel()) 
        
            for i in xrange(self.n):
                models_for_this_state = model_list[i]
                
                for j in xrange(len(models_for_this_state)):
                    models_for_state = models_for_this_state[j]
                    self.models[i].add_model_from_dict(models_for_state)
    
    def _mapB(self,observations):
        self.B_map = numpy.zeros( (self.n,observations.shape[0]), dtype=self.precision)
        
        for i in xrange(self.n):
            self.B_map[i, :] = self.models[i].eval(observations)
        
        themax = numpy.amax(self.B_map.flatten())
        #print ('the maximum is %f') % (themax)

        self.B_map -= themax
        self.B_map[numpy.where(self.B_map < k_min_loglik)] = k_min_loglik
        self.B_map = numpy.exp(self.B_map)

                
    def get_status(self):
        for i in xrange(len(self.models)):
            print "model %d: %s" % (i, self.models[i].get_status())
            
    def _reestimate(self,stats,observations, states):
        #get A and pi
        new_model = _BaseHMM._reestimate(self, stats, observations, states)
        
        gamma = stats['gamma']
        for i in states:
            self.models[i].reestimate(observations, gamma[:, i], self.reestimation_obs)
    
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
    

    
    

    
    

