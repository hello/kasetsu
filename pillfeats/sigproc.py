#!/usr/bin/python
from numpy import *
from numpy.linalg import *
from copy import *
k_trailing = 4
k_sleep_count = 8
k_counts_in_period = 4 * 60 #one minute

def get_counts_per_interval(t, feats, interval):
    N = len(t)
    t1 = t[0]
    count = 1
    output = array([]).reshape((0, 2))
    for i in range(1, N):
        t2 = t[i]
        
        if t2 - t1 > interval:
            output = vstack((output, array([t1, count])))

            t1 = t2
            count = 1
        else:
            count = count + 1
            
    return output

def process_features(feats):
    vecs = feats[:, 0:3]
    mag = feats[:, 3].reshape((feats.shape[0], ))

    angles = zeros((feats.shape[0], ))

    for i in range(1, feats.shape[0]):
        cosang = dot(vecs[i, :], vecs[i-1, :]) / norm(vecs[i, :]) / norm(vecs[i-1, :])
        sinsq = 1 - cosang*cosang
        angles[i] = sinsq
        
    return (angles, mag)
        
def get_features(segs, accelnorm):
    featvecs = array([]).reshape(0, 7)
    num_in_sequence = 0
    maxmax = None
    minmin = None
    normmaxmax = None
    normminmin = None
    times = []
    for k in range(len(segs)):
        seg1 = segs[k]
        x1 = copy(seg1['data'])
        t1 = seg1['t1']
        t2 = seg1['t2']
        
        if k == 0:
            lastt1 = t1
            lastt2 = 0;
            
        if k + 1== len(segs):
            nextt1 = t2
        else:
            nextt1 = segs[k + 1]['t1']

        #normalize
        xn = []
        for i in range(x1.shape[0]):
            x1[i, :] = x1[i, :] * (64.0/accelnorm )
            xn.append(norm(x1[i, :]))
            
            
            
            
        x1 = x1.astype('int')
        lastvec = copy(x1[-1, :])

        #duration in segment.  When it exceeds counts_in_period we save off and reset
        counts_elapsed = nextt1 - lastt1
        
        
        #moving max/min of segment
        themax = amax(x1, axis=0)
        themin = amin(x1, axis=0)
        normmax = amax(array(xn))
        normmin = amin(array(xn))

        
        if (maxmax is None):
            maxmax = themax
        else:
            maxmax = amax(vstack((maxmax, themax)), axis=0)
            
        if (minmin is None):
            minmin = themin
        else:
            minmin = amin(vstack((minmin, themin)), axis=0)
            
        if normmaxmax is None:
            normmaxmax = normmax
        else:
            normmaxmax = amax(vstack((normmaxmax, normmax)), axis=0)
            
        if normminmin is None:
            normminmin = normmin
        else:
            normminmin = amin(vstack((normminmin, normmin)))

            
        if (counts_elapsed > k_counts_in_period):
            #segment has elapsed
         
            maxrange = amax(maxmax-minmin)
            normrange = normmaxmax - normminmin
            time_since_last_update = lastt1 - lastt2
            f = hstack((lastvec, maxrange, normrange,time_since_last_update,  num_in_sequence))

            featvecs = vstack((featvecs, f))
            
            num_in_sequence = 0
            maxmax = None
            minmin = None
            normmaxmax = None
            normminmin = None
            times.append(lastt1 + k_counts_in_period)
            
            
            lastt1 = nextt1
            lastt2 = t2

        else:
            num_in_sequence = num_in_sequence + 1
            
    
    return times, featvecs.astype('int')

def get_features_by_norm_squared(segs):
    featvecs = zeros((1, len(segs)))
    for k in range(len(segs)):
        seg = segs[k]
        x = seg['data']
        maxnormsq = 0
        for j in range(x.shape[0]):
            vec = matrix(x[j, :])
            normsq = vec*vec.transpose()
            if normsq > maxnormsq:
                maxnormsq = normsq
                
        featvecs[0][k] = maxnormsq
        
    return featvecs
    
    
#takes 3xN arrray of accel data
def segment_by_wake_on_motion(x,a_wake,a_sleep):
    state = 0
    if x.shape[1] != 3:
        print ('dim x[:,0] is not 3')
        return None

    N = x.shape[0]
    idx0 = 0
    idx1 = 0
    idx2 = 0
    sleep_count = 0
    
    mysegs = []
    dvec = []
    
    #find sections of wakefulness
    while (idx2 < N):
        v1 = x[idx1, :]
        v2 = x[idx2, :]
        avec = abs(v2-v1)
        d = sum(avec)
        dvec.append(d)
        
        #sleep -- check for wake
        #when you wake, note the index
        if state == 0:
            if d > a_wake:
                state = 1
                idx0 = idx2
                sleep_count = 0
                #print('wake at %d' % idx1)
            
        
        #wake -- check for sleep
        #save off the segment when you sleep
        if state == 1:
          
            if d < a_sleep:
                sleep_count = sleep_count + 1
            
            if sleep_count > k_sleep_count:
                state = 0
                seg = {}
                seg['t1'] = idx0
                seg['t2'] = idx2
                seg['dt'] = idx2-idx0
                seg['data'] = x[idx0:idx2, :]
                
                mysegs.append(seg)
                idx1 = idx2
                #print('sleep at %d' % idx1)

        idx2 = idx2 + 1
        
        if idx1 < idx2 - k_trailing:
            idx1 = idx1 + 1
        
        
    return mysegs





    
