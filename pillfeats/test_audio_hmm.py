#!/usr/bin/python
import numpy
import numpy.linalg
import numpy.random
import hmm.continuous.NormalizedVectorHMM

def gen_hmm(A, thetas, noise, m):
    obs = numpy.zeros((m, 3))
    n = A.shape[0]
    
    s = 0;
    ca = numpy.cumsum(A,axis=1)
    
    for t in xrange(m):
        
        theta = thetas[s]
        obs[t] = theta + numpy.random.randn(theta.shape[0])*noise
        obs[t] = obs[t] / numpy.linalg.norm(obs[t])
        p = numpy.random.rand()
        
        #cumm probs
        cp = ca[s][:]
        
        #first one it's less than
        p2 = p <= cp
        for s2 in range(len(p2)):
            if p2[s2] == True:
                break
        
        s = s2
        
        
    return obs
    

if __name__ == '__main__':
    numpy.set_printoptions(precision=3, suppress=True, threshold=numpy.nan)
    #test this
    n = 2
    d = 3
    A = numpy.array([[0.75, 0.25], [0.10, 0.90]])
    Ai = numpy.array([[0.95, 0.05], [0.05, 0.95]])

    v1 = numpy.array([1, 1, 0]);
    v2 = numpy.array([0.1, 1, 0]);
    v1 = v1 / numpy.linalg.norm(v1)
    v2 = v2 / numpy.linalg.norm(v2)

    v1i = numpy.array([1.2, 0.9, 0]);
    v2i = numpy.array([-0.2, 1.3, 0.1]);
    v1i = v1i / numpy.linalg.norm(v1i)
    v2i = v2i / numpy.linalg.norm(v2i)

    thetas = [v1, v2]
    thetasi = [v1i, v2i]
    
    obs = gen_hmm(A, thetas, 0.1, 10000)
   
    pi = numpy.zeros((n, ))
    pi[0] = 0.99
    pi[1] = 0.01
    
    print ('\n\ninitial values')
    print thetas[0]
    print thetas[1]

    print ('\n\nvectors')
    print v1
    print v2
    hmm = hmm.continuous.NormalizedVectorHMM.NormalizedVectorHMM(n,d,Ai,pi,thetasi)
    
    hmm.train(obs, 10)
    print ('\n\nA')
    print hmm.A
    
    print ('\n\nthetas')
    print hmm.thetas
