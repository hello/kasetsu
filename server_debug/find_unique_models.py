#!/usr/bin/python
import online_hmm_pb2
import numpy as np
import numpy.linalg as linalg
import sys
from matplotlib.pyplot import *
import sklearn.cluster

np.set_printoptions(precision=4,suppress=True,linewidth=10000)
MAX_DIMS = 4
k_cutoff_threshold = 0.98

def get_matrix(inmtx):
    M = inmtx.num_rows
    N = inmtx.num_cols

    k = 0;
    mtx = np.zeros((M,N))
    for j in range(M):
        for i in range(N):
            mtx[j,i] = inmtx.data[k]
            k += 1
    

    return mtx

def model_obs_to_dict(model,modelid):
    mydict = {}
    for i in range(len(model.log_observation_model_ids)):
        mydict[model.log_observation_model_ids[i]] = get_matrix(model.log_observation_model_numerator[i])

    denom = model.log_denominator
    
    for key in mydict:
        mtx = mydict[key]
        for j in range(mtx.shape[0]):
            mtx[j,:] -= denom[j]
            if np.any(mtx[j,:] > 100):
                print 'invalid model: ' + modelid
                return None
                
            mtx[j,:] = np.exp(mtx[j,:])
            
            thesum = np.sum(mtx[j,:] ** 2) ** 0.5
            mtx[j,:] /= thesum

                        

    return mydict

def models_to_dict(models):
    mymodels = {}
    for model in models:
        output_id = int(model.output_id)
        model_id = model.id
        if not mymodels.has_key(output_id):
            mymodels[output_id] = {}

        model_dict = model_obs_to_dict(model,model_id)

        if model_dict != None:
            mymodels[output_id][model_id] = model_dict

    return mymodels
        

def save_models(models_list):
    protobuf = online_hmm_pb2.AlphabetHmmUserModel()
    for model in models_list:
        newmodel = protobuf.models.add()
        newmodel.MergeFrom(model)

    print 'saving to independent.model'
    f = open('independent.model','w')
    f.write(protobuf.SerializeToString())
    f.close()


def load_models(filename):
    protobuf = online_hmm_pb2.AlphabetHmmUserModel()
    f = open(filename,'r')
    protobuf.ParseFromString(f.read())
    f.close()
    return protobuf.models


def compare_models(model1,model2):

    dotsum = 0.0
    count = 0
    for key in model1:
        if model2.has_key(key):
            
            m1 = model1[key]
            m2 = model2[key]

            for j in range(m1.shape[0]):
                dotprod = np.dot(m1[j,:],m2[j,:])
                dotsum += dotprod
                count += 1

        else:
            print 'KEY MIS-MATCH!!!!'


    return dotsum / count
            

    
def get_matrix_laplacian(A):
    d = np.diagonal(A)
    D = np.matrix(np.zeros(A.shape))
    for i in range(A.shape[0]):
        D[i,i] = np.sum(A[i,:])
        D[i,i] = D[i,i] ** -0.5

    L = np.identity(A.shape[0]) - D * A * D

    return L

def main():
    protobuf_models = load_models(sys.argv[1])
    models = models_to_dict(protobuf_models)

    print '\n'

    models_list = []
    
    for output_id in models:
        models_for_this_output = models[output_id]


        keys =  models_for_this_output.keys()

        N = len(keys)

        A = np.zeros((N,N))
        
        for j in range(N):
            for i in range(j + 1):

                A[j,i] = compare_models(models_for_this_output[keys[j]],models_for_this_output[keys[i]])

                if A[j,i] < k_cutoff_threshold:
                    A[j,i] = 0.0
                else:
                    A[j,i] = 1.0;
                    
                A[i,j] = A[j,i]                

        L = get_matrix_laplacian(np.matrix(A))
        eigenval,eigenvec = linalg.eig(L)

        idx = eigenval.argsort()   
        eigenval = eigenval[idx]
        eigenvec = eigenvec[:,idx]

        z, = np.where(np.abs(eigenval) < 1e-3)

        zmax = z[-1]

        num_dims = np.min([MAX_DIMS,zmax])

        print 'using %d dimensions' % num_dims
        
        U = np.array(eigenvec[:,0:num_dims])

        for j in range(U.shape[0]):
            row = U[j,:]
            thesum =  np.sum(row ** 2)

            if thesum > 1e-10:
                U[j,:] /= np.sqrt(thesum)


        
        kmeans = sklearn.cluster.KMeans()
        kmeans.fit(U)
        groups = kmeans.predict(U)

        num_groups = np.max(groups)

        print 'FOUND %d GROUPS!' % num_groups

        group_keys = {}

        for i in range(num_groups + 1):
            group_keys[i] = []

        for i in range(len(groups)):
            group_keys[groups[i]].append(keys[i])


        independent_items = []
        for item_key in group_keys:
            item = group_keys[item_key]
            if len(item) > 0:
                independent_items.append(item[0])

        print independent_items
                
        for m in protobuf_models:
            if m.id in independent_items:
                print m.id
                models_list.append(m)

    save_models(models_list)

if __name__ == '__main__':
    main()


    
