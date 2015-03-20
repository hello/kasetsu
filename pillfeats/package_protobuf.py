#!/usr/bin/python

import sleep_hmm_pb2
import sys
import base64
import sys
import json
from time import strftime
import numpy

from hmm.continuous.CompositeModelHMM import CompositeModelHMM


def to_proto(composite_hmm,aux_params, input_filename):
    
    on_bed_states = aux_params['on_bed_states']   
    sleep_states = aux_params['sleep_states']  
    natural_light_filter_start_hour = aux_params['natural_light_filter_start_hour']
    natural_light_filter_stop_hour = aux_params['natural_light_filter_stop_hour']
    num_model_params = aux_params['num_model_params']
    users = aux_params['users'] 
    model_name = aux_params['model_name']
    audio_disturbance_threshold_db = aux_params['audio_disturbance_threshold_db']
    pill_magnitude_disturbance_threshold_lsb = aux_params['pill_magnitude_disturbance_threshold_lsb']
    enable_interval_search = aux_params['enable_interval_search']
    
    
    sleep_hmm = sleep_hmm_pb2.SleepHmm()
    
    sleep_hmm.source = input_filename
    sleep_hmm.user_id = users
    sleep_hmm.model_name = model_name
    sleep_hmm.audio_disturbance_threshold_db = audio_disturbance_threshold_db
    sleep_hmm.pill_magnitude_disturbance_threshold_lsb = pill_magnitude_disturbance_threshold_lsb
    sleep_hmm.num_model_params = num_model_params
    sleep_hmm.natural_light_filter_start_hour = natural_light_filter_start_hour
    sleep_hmm.natural_light_filter_stop_hour = natural_light_filter_stop_hour
    sleep_hmm.enable_interval_search = enable_interval_search
    
    Nstates = len(composite_hmm.models)
    
    sleep_hmm.num_states = Nstates
    amat = numpy.array(composite_hmm.A).flatten().tolist()
    
    for entry in amat:
        sleep_hmm.state_transition_matrix.append(entry)
        
    pimat = numpy.array(composite_hmm.pi).flatten().tolist()
    
    for entry in pimat:
        sleep_hmm.initial_state_probabilities.append(entry)
    
    for i in xrange(Nstates):
        
        m_state = sleep_hmm.states.add()

        model =  composite_hmm.models[i]
        d = model.to_dict()
                
        m_light = sleep_hmm_pb2.GammaModel()
        m_light.mean = d[0]['model_data']['mean']
        m_light.stddev = d[0]['model_data']['stddev']
        
        m_motion_count = sleep_hmm_pb2.PoissonModel()
        m_motion_count.mean = d[1]['model_data']['mean']

        m_disturbances = sleep_hmm_pb2.DiscreteAlphabetModel()
        vec = d[2]['model_data']['alphabet_probs']
        for v in vec:
            m_disturbances.probabilities.append(v)
            
        m_soundcounts = sleep_hmm_pb2.GammaModel()
        m_soundcounts.mean = d[3]['model_data']['mean']
        m_soundcounts.stddev = d[3]['model_data']['stddev']

        m_natural_light_filter = sleep_hmm_pb2.DiscreteAlphabetModel()
        vec = d[4]['model_data']['alphabet_probs']
        for v in vec:
            m_natural_light_filter.probabilities.append(v)

        m_state.light.MergeFrom(m_light)
        m_state.motion_count.MergeFrom(m_motion_count)
        m_state.disturbances.MergeFrom(m_disturbances)
        m_state.log_sound_count.MergeFrom(m_soundcounts)
        m_state.natural_light_filter.MergeFrom(m_natural_light_filter)
        
        if i in sleep_states:
            m_state.sleep_mode = sleep_hmm_pb2.SLEEP
        else:
            m_state.sleep_mode = sleep_hmm_pb2.WAKE

        if i in on_bed_states:
            m_state.bed_mode = sleep_hmm_pb2.ON_BED
        else:
            m_state.bed_mode = sleep_hmm_pb2.OFF_BED
           
        '''
        if i in light_sleep_state:
            m_state.sleep_depth = sleep_hmm_pb2.LIGHT
        elif i in regular_sleep_state:
            m_state.sleep_depth = sleep_hmm_pb2.REGULAR
        elif i in disturbed_sleep_state:
            m_state.sleep_depth = sleep_hmm_pb2.DISTURBED
        else:
            m_state.sleep_depth = sleep_hmm_pb2.NOT_APPLICABLE
        '''
        m_state.sleep_depth = sleep_hmm_pb2.NOT_APPLICABLE

        
    
    return sleep_hmm
    
        
    
if __name__ == '__main__':
    n = len(sys.argv)
    

    if n <= 1:
        print 'no aguments specified'
        sys.exit(0)
    
    outfilename = strftime("HMMSET_%Y-%m-%d_%H:%M:%S.proto")

    all_models = sleep_hmm_pb2.SleepHmmModelSet()
    
    for i in xrange(1, n):
        model_filename = sys.argv[i]
        
        #open file and get model
        f = open(model_filename, 'r')
        model_data = json.load(f)
        f.close()
        
        default_model_data = model_data['default']

        
        hmm = CompositeModelHMM()
        hmm.from_dict(default_model_data)


        hmm_model_protobuf = to_proto(hmm,default_model_data['params'], model_filename)
        all_models.models.extend([hmm_model_protobuf])
    
    serialized_model_string = base64.b64encode(all_models.SerializeToString())
    f = open(outfilename, 'w')
    f.write(serialized_model_string)
    f.close()
    print 'Wrote to ',outfilename
