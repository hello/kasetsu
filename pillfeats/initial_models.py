
from hmm.continuous.CompositeModelHMM import CompositeModelHMM
import numpy as np

def make_poisson(mean, obsnum):
    return {'model_type' : 'poisson' ,  'model_data' : {'obs_num' : obsnum, 'mean' : mean}}
    
def make_uniform(mean, obsnum):
    return {'model_type' : 'uniform' ,  'model_data' : {'obs_num' : obsnum, 'mean' : mean}}
    
def make_discrete(dists, obsnum):
    return {'model_type' : 'discrete_alphabet' ,  'model_data' : {'obs_num' : obsnum,  'alphabet_probs' : dists, 'allow_reestimation' : True}}
    
def make_penalty(dists, obsnum):
    return {'model_type' : 'discrete_alphabet' ,  'model_data' : {'obs_num' : obsnum,  'alphabet_probs' : dists, 'allow_reestimation' : False}}
    
    
def make_gamma(mean, stddev, obsnum):   
    return {'model_type' : 'gamma' ,  'model_data' : {'obs_num' : obsnum, 'mean' : mean,  'stddev' : stddev}}

def get_default_model():
    
        
    low_light = 0.1
    med_light = 3.0
    high_light = 6.0
    low_light_stddev = 1.0
    high_light_stddev = 2.5
    
    no_motion = 0.01
    low_motion = 3.0
    med_motion = 4.0
    high_motion = 8.0
    

    low_wave = [0.9, 0.1]
    high_wave = [0.1, 0.9]
   
    sc_low = 1.0
    sc_high = 2.0
    sc_low_stddev = 0.5
    sc_high_stddev = 1.0
    
    no_penalty = [1., 1.]
    yes_penalty = [1., 1e-6]
    
    #states
    # 0 - off bed #1 (very low activity,low light)
    # 1 - off bed #2 (very low activity,high light)
    # 2 - reading on bed (high activity, high light)
    # 3 - ipad on bed    (high activity, low light)
    # 4 - sleep (low activity, low light)
    # 5 - disturbed sleep (high activity, low light)
    # 7 - waking up with alarm (med light, med activity, high wave)
    # 8 - woken up (med light, high activity) 
    
    A = np.array([
    
    [0.65, 0.10, 0.10, 0.10,   0.10,  0.10,   0.00, 0.00, 0.00,   0.00, 0.00], 
    [0.10, 0.65, 0.10, 0.10,   0.10,  0.10,   0.00, 0.00, 0.00,   0.00, 0.00], 
    [0.10, 0.10, 0.65, 0.10,   0.10,  0.10,   0.00, 0.00, 0.00,   0.00, 0.00], 
    [0.10, 0.10, 0.10, 0.65,   0.10,  0.10,   0.00, 0.00, 0.00,   0.00, 0.00], 
    
    [0.05, 0.05, 0.05, 0.05,   0.70, 0.10,    0.10, 0.00, 0.00,   0.00, 0.00], 
    [0.05, 0.05, 0.05, 0.05,   0.10, 0.70,    0.10, 0.00, 0.00,   0.00, 0.00], 
    
    [0.00, 0.00, 0.00, 0.00,   0.00,  0.05,   0.55, 0.10, 0.05,   0.10, 0.10], 
    [0.00, 0.00, 0.00, 0.00,   0.00,  0.05,   0.45, 0.50, 0.00,   0.00, 0.00], 
    [0.10, 0.00, 0.10, 0.00,   0.05,  0.00,   0.00, 0.00, 0.65,   0.10, 0.10], 
    
    [0.10, 0.10, 0.10, 0.10,   0.00, 0.00,    0.00, 0.00, 0.00,   0.60, 0.10], 
    [0.10, 0.10, 0.10, 0.10,   0.00, 0.00,    0.00, 0.05, 0.00,   0.10, 0.55]
    ])
             
             
    pi0 = np.ones((A.shape[0], )) / A.shape[0]
        
    #light, then counts, then waves, then sound, then energy
       

    model0 = [make_gamma(high_light,high_light_stddev, 0), make_poisson(no_motion, 1),     make_discrete(low_wave, 2),    make_gamma(sc_high, sc_high_stddev, 3), make_penalty(no_penalty, 4)]
    model1 = [make_gamma(low_light,low_light_stddev, 0),   make_poisson(no_motion, 1),     make_discrete(low_wave, 2),    make_gamma(sc_high, sc_high_stddev, 3), make_penalty(no_penalty, 4)]
    model2 = [make_gamma(high_light,high_light_stddev, 0), make_poisson(no_motion, 1),     make_discrete(low_wave, 2),    make_gamma(sc_low, sc_low_stddev, 3),   make_penalty(no_penalty, 4)]
    model3 = [make_gamma(low_light,low_light_stddev, 0),   make_poisson(no_motion, 1),     make_discrete(low_wave, 2),    make_gamma(sc_low, sc_low_stddev, 3),   make_penalty(no_penalty, 4)]
    
    model4 = [make_gamma(high_light,high_light_stddev, 0), make_poisson(high_motion, 1),   make_discrete(high_wave, 2),   make_gamma(sc_high, sc_high_stddev, 3), make_penalty(no_penalty, 4)]
    model5 = [make_gamma(low_light,low_light_stddev, 0),   make_poisson(high_motion, 1),   make_discrete(high_wave, 2),   make_gamma(sc_high, sc_high_stddev, 3), make_penalty(no_penalty, 4)]

    model6 = [make_gamma(low_light,low_light_stddev, 0),   make_poisson(low_motion, 1),    make_discrete(low_wave, 2),    make_gamma(sc_low, sc_low_stddev, 3),   make_penalty(no_penalty, 4)]
    model7 =[make_gamma(low_light,low_light_stddev, 0),    make_poisson(low_motion, 1),    make_discrete(low_wave, 2),    make_gamma(sc_high, sc_high_stddev, 3), make_penalty(no_penalty, 4)]
    model8 = [make_gamma(high_light,high_light_stddev, 0), make_poisson(low_motion, 1),    make_discrete(low_wave, 2),    make_gamma(sc_low, sc_low_stddev, 3),   make_penalty(yes_penalty, 4)]
    
    model9 = [make_gamma(high_light,high_light_stddev, 0), make_poisson(high_motion, 1),   make_discrete(high_wave, 2),   make_gamma(sc_high, sc_high_stddev, 3), make_penalty(no_penalty, 4)]
    model10 = [make_gamma(low_light,low_light_stddev, 0),  make_poisson(high_motion, 1),   make_discrete(high_wave, 2),   make_gamma(sc_high, sc_high_stddev, 3), make_penalty(no_penalty, 4)]

    
    
    models = [model0, model1, model2, model3, model4,model5, model6, model7, model8, model9, model10]

    hmm = CompositeModelHMM(models, A, pi0, verbose=True)
    
    return hmm
