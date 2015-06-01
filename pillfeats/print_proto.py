#!/usr/bin/python

import sleep_hmm_pb2
import sys

def print_state(state,statenum):
    light = state.light
    mot = state.motion_count
    dist = state.disturbances
    sound = state.log_sound_count
    nat = state.natural_light_filter

    printstr = '%02d: gam: %f,%f   psn: %f,  alph: %f,%f  gam: %f,%f, alph: %f,%f' % (statenum,light.mean,light.stddev,mot.mean,dist.probabilities[0],dist.probabilities[1],sound.mean,sound.stddev,nat.probabilities[0],nat.probabilities[1])
    print printstr

def get_vec_as_mat(A,N):
    k = 0;
    mat = []
    for row in range(N):
        mat.append([])
        
        for col in range(N):
            mat[row].append(A[k])
            k += 1

    return mat

if __name__ == '__main__':

    f = open(sys.argv[1]);
    s = f.read();
    f.close()
    q = sleep_hmm_pb2.SleepHmmModelSet()
    q.ParseFromString(s.decode('base64'))

    for model in q.models:
        print "name=%s" % model.model_name

        N = model.num_states
        print "%d states" % N
        
        A = model.state_transition_matrix
        mat = get_vec_as_mat(A,N)
        for row in mat:
            print ",".join(['%05.3f' % item for item in row])

        statenum = 0
        for state in model.states:
            print_state(state,statenum)
            statenum += 1

        print '\n\n'
