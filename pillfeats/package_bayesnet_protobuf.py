#!/usr/bin/python

import sleep_hmm_bayesnet_pb2
import beta_binomial_pb2
import sys
import base64
import sys
import json
from time import strftime
import numpy


use_wave_as_disturbance = True
natural_light_filter_start_hour = 16.0
natural_light_filter_stop_hour = 4.0
pill_magnitude_disturbance_threshold_lsb = 15000
enable_interval_search = False
meas_period = 5

k_num_measurements_for_prior = 5.0

obs_strings_to_enums = {'light' : sleep_hmm_bayesnet_pb2.LOG_LIGHT,
           'sound' : sleep_hmm_bayesnet_pb2.LOG_SOUND,
           'duration' : sleep_hmm_bayesnet_pb2.MOTION_DURATION,
           'natlight' : sleep_hmm_bayesnet_pb2.NATURAL_LIGHT,
           'pill_disturbance' : sleep_hmm_bayesnet_pb2.PILL_MAGNITUDE_DISTURBANCE,
            'wave_disturbance' : sleep_hmm_bayesnet_pb2.WAVE_DISTURBANCE,
        'light_disturbance' : sleep_hmm_bayesnet_pb2.LIGHT_INCREASE_DISTURBANCE,
        'sound_disturbance' : sleep_hmm_bayesnet_pb2.SOUND_INCREASE_DISTURBANCE}

def get_obs_model(model,state_idx,obs_type,obs):
    obs.state_index = state_idx
    obs.meas_type.append(obs_strings_to_enums[obs_type])
    
    model_type = model['model_type']
    model_data = model['model_data']
    
    if model_type == 'chisquare':
        m = sleep_hmm_bayesnet_pb2.ChiSquareModel()
        m.mean = model_data['mean']
        obs.chisquare.MergeFrom(m)

    elif model_type == 'gaussian':
        m = sleep_hmm_bayesnet_pb2.OneDimensionalGaussianModel()
        m.mean = model_data['mean']
        m.stddev = model_data['stddev']
        obs.gaussian.MergeFrom(m)
        
    elif model_type == 'gamma':
        m = sleep_hmm_bayesnet_pb2.GammaModel()
        m.mean = model_data['mean']
        m.stddev = model_data['stddev']
        obs.gamma.MergeFrom(m)
        
    elif model_type == 'poisson':
        m = sleep_hmm_bayesnet_pb2.PoissonModel()
        m.mean = model_data['mean']
        obs.poisson.MergeFrom(m)

    elif model_type == 'discrete_alphabet':
        m = sleep_hmm_bayesnet_pb2.DiscreteAlphabetModel()
        probs = model_data['alphabet_probs']
        for p in probs:
            m.probabilities.append(p)

        obs.alphabet.MergeFrom(m)

    else:
        return False

    return True
        
def get_probs_from_params(params):
    keys = params.keys()

    prob_keys = []
    for key in keys:
        if key.startswith('p_'):
            prob_keys.append(key)

    mydict = {}
    for key in prob_keys:
        probs = params[key]
        mydict[key] = probs

    return mydict

def place_condprobs(bayesnet,probdict,model_id,num_measurements_for_prior):
    for key in probdict:
        probs =  probdict[key]

        cp = bayesnet.conditional_probabilities.add()

        cp.model_id = model_id
        cp.output_id = key

        for p in probs:
            bcp = cp.probs.add()
            bcp.alpha = p * num_measurements_for_prior
            bcp.beta = (1.0 - p) * num_measurements_for_prior
    
def to_proto(input_filenames):
    
    meas_params = sleep_hmm_bayesnet_pb2.MeasurementParams()
    
    meas_params.motion_count_for_disturbances = pill_magnitude_disturbance_threshold_lsb
    meas_params.natural_light_filter_start_hour = natural_light_filter_start_hour
    meas_params.natural_light_filter_stop_hour = natural_light_filter_stop_hour
    meas_params.enable_interval_search = enable_interval_search
    meas_params.num_minutes_in_meas_period = meas_period
    meas_params.use_waves_for_disturbances = use_wave_as_disturbance


    bayes_net = sleep_hmm_bayesnet_pb2.HmmBayesNet()

    bayes_net.measurement_parameters.MergeFrom(meas_params)


    for filename in input_filenames:
        hmm = bayes_net.independent_hmms.add()
        
        f = open(filename,'rb')
        data = json.load(f)
        f.close()

        data = data['default']
        models = data['models']
        params = data['params']
        model_id = params['model_name']
        
        if params.has_key('num_measurements_for_prior'):
            num_measurements_for_prior = params['num_measurements_for_prior']
        else:
            num_measurements_for_prior = k_num_measurements_for_prior

        obs_map = params['obs_map']

        probdict = get_probs_from_params(params)        
        place_condprobs(bayes_net,probdict,model_id,num_measurements_for_prior)
        
        if len(models) != len(data['A']):
            print ('ERROR state transition matrix dimensions did not match the number of models')
            sys.exit(0)

        hmm.num_states = len(models)
        
        amat = numpy.array(data['A']).flatten().tolist()
            
        for entry in amat:
            hmm.state_transition_matrix.append(entry)

        hmm.id = model_id
        hmm.description = filename

        #time to deal with observation models
        for istate in range(len(models)):
            model = models[istate]

            for m in model:
                obs_type = obs_map[m['model_data']['obs_num']]       
                if get_obs_model(m,istate,obs_type,hmm.observation_model.add()) == False:
                    print m
                    print 'found a model that I could not interpret'
                    sys.exit(0)

    return bayes_net
    
        
    
if __name__ == '__main__':
    n = len(sys.argv)
    

    if n <= 1:
        print 'no aguments specified'
        sys.exit(0)
    
    outfilename = strftime("BAYESNET_%Y-%m-%d_%H:%M:%S.proto")

    bayesnet_protobuf = to_proto(   sys.argv[1:n])
    
    serialized_model_string = base64.b64encode(bayesnet_protobuf.SerializeToString())
    f = open(outfilename, 'w')
    f.write(serialized_model_string)
    f.close()
    print 'Wrote to ',outfilename
