#!/usr/bin/python
import numpy
import numpy.linalg
import numpy.random
from scipy.stats import poisson

def fit_poisson(n_components, x, n_iter):
    #data must be 1-d
    max = numpy.amax(x)
    min = numpy.amin(x)
    
    means = []
    for i in xrange(n_components):
        means.append(numpy.random.rand() * (max - min) + min)
    
    mixture_weights = numpy.ones((n_components, )) / n_components
    
    
    
    for iter in xrange(n_iter):
        evals = []
        
        psn = []
        for i in xrange(n_components):
            psn.append(poisson(means[i]))
        
        for i in xrange(n_components):
            #y = p(x | theta), theta are params (means)
            y = psn[i].pmf(numpy.array(x))
            evals.append(y.copy())
            
        weights = numpy.zeros((n_components, len(x)))
        
        for t in xrange(len(x)):
            numerator = numpy.zeros((n_components, ))
            for i in xrange(n_components):
                numerator[i] = evals[i][t] * mixture_weights[i]
                
            denom = numpy.sum(numerator)
            
            for i in xrange(n_components):
                weights[i][t] = numerator[i] / denom
        
        #new mixture weights by frequentist counting
        mixture_counts = numpy.sum(weights, axis=1)
        mixture_weights = mixture_counts / len(x)
        #new means by counting, again
        temp = weights * numpy.tile(x, (n_components, 1))
        means = numpy.sum(temp, axis=1) / mixture_counts

    #sort ascending by mean
    indices = range(len(means))
    indices.sort(key=means.__getitem__)
    
    means_out = means[indices]
    mixture_weights_out = mixture_weights[indices]
    
    return means_out, mixture_weights_out
    
    

if __name__ == '__main__':
    
    x = numpy.load('flat_seg.npy')
    means, weights = fit_poisson(2, x, 20)
    print means, weights
    
    

    
