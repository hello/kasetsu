#!/usr/bin/python
import clusterfeats
import hmm.continuous.NormalizedVectorHMM
import numpy
import numpy.linalg
import sys
import json

k_feat_vec_len = 16
k_num_iters = 20

def fit_model(filename, n_clusters, similarity_threshold):
    clusterer = clusterfeats.AudioFeatureClustering()
    clusterer.set_data(filename)
    clusterer.compute_cluster_means(n_clusters, similarity_threshold)
    
    vecs = clusterer.vectors
    
    thetas = []
    var = 0.1
    for v in vecs:
        v2 = numpy.array(v)[0]
        v2 = v2 / numpy.linalg.norm(v2)
        thetas.append([v2, var])
        
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
        
        
    myhmm = hmm.continuous.NormalizedVectorHMM.NormalizedVectorHMM(n_clusters, k_feat_vec_len, Ai, pi, thetas)
        
    
    obs = numpy.array(clusterer.x)
    
    myhmm.train(obs, k_num_iters)
    
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
