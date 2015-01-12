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
k_outer_loop_iters = 1
vs = []
#vs.append([-0.735,  0.008, -0.289,  0.196, -0.133, -0.329, -0.196,  0.039,  0.086,  0.368, -0.141, -0.063, -0.063,  0.031, -0.016,  0.   ])
#vs.append([-0.876,  0.098, -0.419,  0.165, -0.127,  0.009, -0.004, -0.03 , -0.023,  0.017, -0.028, -0.014, -0.002, -0.001, -0.015, -0.003])

def fit_model(filename, n_clusters, similarity_threshold):
    
            
    count = 0
    while True:
        
        clusterer = clusterfeats.AudioFeatureClustering()
        clusterer.set_data(filename)
        clusterer.compute_cluster_means(n_clusters, similarity_threshold)
        
        vecs = clusterer.vectors
        
        thetas = []
        var = 0.5
        for i in range(n_clusters):
            v = 2.0 * numpy.random.rand(k_feat_vec_len) - 1.0
            #v = numpy.array(vs[i]).reshape((k_feat_vec_len, 1))
            v = v / numpy.linalg.norm(v)
            #v = vecs[i].reshape((k_feat_vec_len, 1))
            thetas.append([v, var])
            
        Ai = numpy.zeros((n_clusters, n_clusters))
        pi = numpy.zeros((n_clusters, ))
        
        Ai[:][:] = 0.4 / (n_clusters - 1)
        
        
        for i in range(n_clusters):
            Ai[i][i] = 0.6
            
        pi[:] = 0.5 / (n_clusters - 1)
        pi[0] = 0.5
            
            
        #print 'theta initial'
        #for theta in thetas:
        #    print theta
            

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
        for theta in myhmm.thetas:
            print theta

        if not isbad or count > k_outer_loop_iters:
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
