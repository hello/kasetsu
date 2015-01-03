#!/usr/bin/python
import numpy
import numpy.linalg
import hmm.continuous.NormalizedVectorHMM

if __name__ == '__main__':
    #test this
    n = 2
    d = 3
    A = numpy.array([[0.80, 0.20], [0.20, 0.80]])
    
    v1 = numpy.array([1, 1, 0])/numpy.sqrt(2)
    v2 = numpy.array([0, 0, -1])/numpy.sqrt(2)
    
    v1i = numpy.array([0.9, 0.8, 0.3])
    v1i = v1i / numpy.linalg.norm(v1i)
    
    v2i = numpy.array([1.2, 0.2, -0.5])
    v2i = v2i / numpy.linalg.norm(v2i)
    
    thetas = [v1i, v2i]
    
    obs = numpy.zeros((20, 3))

    for t in range(0, 20):
        if t % 3 == 0:
            obs[t] = v1
        else:
            obs[t] = v2
        
    
    pi = numpy.zeros((n, ))
    pi[0] = 0.90
    pi[1] = 0.10
    
    print ('\n\ninitial values')
    print thetas[0]
    print thetas[1]

    print ('\n\nvectors')
    print v1
    print v2
    hmm = hmm.continuous.NormalizedVectorHMM.NormalizedVectorHMM(n,d,A,pi,thetas)
    
    hmm.train(obs, 10)
    print ('\n\nA')
    print hmm.A
    
    print ('\n\nthetas')
    print hmm.thetas
