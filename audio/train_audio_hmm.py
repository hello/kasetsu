#!/usr/bin/python
import clusterfeats
import hmm.continuous.NormalizedVectorHMM
import numpy
import numpy.linalg
import numpy.random
import sys
import json

k_feat_vec_len = 16
k_num_iters = 25

def fit_model(filename, n_clusters, similarity_threshold):
    
            
    count = 0
    while True:
        
        clusterer = clusterfeats.AudioFeatureClustering()
        clusterer.set_data(filename)
        clusterer.compute_cluster_means(n_clusters, similarity_threshold)
        
        vecs = clusterer.vectors
        
        thetas = []
        var = 0.1
        for i in range(n_clusters):
            v = 2.0 * numpy.random.rand(k_feat_vec_len) - 1.0
            v = v / numpy.linalg.norm(v)
            thetas.append([v, var])
            
        Ai = numpy.zeros((n_clusters, n_clusters))
        pi = numpy.zeros((n_clusters, ))
        
        Ai[:][:] = 0.2 / (n_clusters - 1)
        
        
        for i in range(n_clusters):
            Ai[i][i] = 0.8
            
        pi[:] = 0.1 / (n_clusters - 1)
        pi[0] = 0.9
            
            
        print 'theta initial'
        for theta in thetas:
            print theta
            

        obs = numpy.array(clusterer.x)

        print 'iter %d' % count
        myhmm = hmm.continuous.NormalizedVectorHMM.NormalizedVectorHMM(n_clusters, k_feat_vec_len, Ai, pi, thetas)
        myhmm.train(obs, k_num_iters)
    
        isbad = False
        for j in range(myhmm.n):
            if myhmm.A[j][j] < 0.2:
                isbad = True
                
        count = count + 1
        
        print myhmm.A

        if not isbad or count > 100:
            break;
    
    
    print ('results:')
    
    print myhmm.A
    print myhmm.pi
    
    for theta in myhmm.thetas:
        print theta
    
    
    hmm_data = myhmm.to_dict()
    hmm_json = json.dumps(hmm_data)
    fs = filename.split('.')
    print fs
    outfile = '%s.hmm' % fs[0]
    print 'writing to %s' % outfile
    f = open(outfile, 'w')
    f.write(hmm_json)
    f.close()
    
if __name__ == '__main__':
    fit_model(sys.argv[1], int(sys.argv[2]), float(sys.argv[3]))
