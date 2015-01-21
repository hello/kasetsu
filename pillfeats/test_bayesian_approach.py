#!/usr/bin/python
import pillcsv
import sensecsv
import surveycsv
import all_data
import os.path
import json
from numpy import *
from pylab import *
import sklearn.mixture
import sys
october_1_2014_unix_time = 1412121600.0

pill_data_filename = 'csv/pill_data_2014_12_08.csv'
light_data_filename = 'csv/light_data_2014_12_08.csv'
survey_data_filename = 'csv/sleep_survey_2014_12_19.csv'

save_filename = 'savedata_for_bayes.json'

min_count_pill_data = 250
 
def pull_data():
    
    if not os.path.isfile(save_filename):
        print 'loading data from csv'
        survey_dict = surveycsv.read_survey_data(survey_data_filename,october_1_2014_unix_time )
        pill_dict = pillcsv.read_pill_csv(pill_data_filename,october_1_2014_unix_time)
        sense_dict = sensecsv.read_sense_csv(light_data_filename, october_1_2014_unix_time)
        
        
        data = {'survey' : survey_dict,  'pill' : pill_dict,  'sense' : sense_dict}
        
        f = open(save_filename, 'w')
        json.dump(data, f)
        f.close()
    else:
        print 'loading data from %s' % save_filename
        f = open(save_filename)
        data = json.load(f)
        f.close()
    
    data2 = all_data.join_by_account_id(data, min_count_pill_data)
        
    for key in data2:
        if data['survey'].has_key(key):
            data2[key]['survey'] = data['survey'][key]
    
    return data2


def get_dt_list(d):
    dt_list = []
    m_list = []
    for key in d:
        t = array(d[key]['pill'][0])
        m = array(d[key]['pill'][1])
        dt = diff(t)
        m2 = m[1:]
        dt_list.extend(dt)
        m_list.extend(m2)
        #plot((t - t[0])/60.0/60.0, m,'.-')
        #show()
        
    dt_list = array(dt_list);

    #dt_list = delete(dt_list,where(dt_list > 86400))
    idx = where(dt_list < 0)
    dt_list = delete(dt_list,idx)
    m_list = delete(m_list, idx)
    dt_list = dt_list / 60.0; #convert to minutes
    dt_list = ceil(dt_list)
    
    return array(dt_list), array(m_list)

def do_gmm(x, n, mytitle, plotme = False):
    gmm = sklearn.mixture.GMM(n_components=n, covariance_type='full')
    gmm.fit(x)

    print 'means'
    print gmm.means_
    print 'covariances'
    print gmm.covars_
    print 'weights'
    print gmm.weights_
    
    y = gmm.predict(x)
    print x.shape
    
    if plotme:
        if len(x.shape) == 1:
            g = [x[where(y==i)] for i in xrange(n)]
    
            figure(1)
    
            for gg in g:
                plot(gg,'.')
                
            grid('on')
            title(mytitle + ': classification')
    
            
            figure(2)
            hist(x, 50)
            title(mytitle + ': data distribution')
            show()
    
        elif x.shape[1] == 2:
            g = [x[where(y==i), :] for i in xrange(n)]
    
            for gg in g:
                plot(gg[0, :, 0], gg[0, :, 1],'.')
                
            grid('on')
            show()
            
    return (gmm.means_, gmm.covars_, gmm.weights_)
        
    
#assume 1-d likelihood function
def evaluate_log_likelihood(params, x):
    evals = []
    means, covars, weights = params
    nmodels = len(weights)
    for i in xrange(nmodels):

        m  = array(means[i])
        P = array(covars[i])
        w = array(weights[i])
        
        #x2 could be a list
        x2 = x - m
        r = -0.5 * x2 / P * x2
        r -= log(sqrt(P))
        r += log(w)
        #return log liklihoods
        #eval = exp(r) / sqrt(P)
        evals.append(r)
        
    return evals
    
if __name__ == '__main__':
    set_printoptions(precision=3, suppress=True, threshold=np.nan)
    max_dt = 180 #minutes
    min_m = 10.0

    d = pull_data()
    dt_list, m_list = get_dt_list(d)
    
    idx = where(dt_list > max_dt)
    no_tail_dt = delete(dt_list, idx)
    no_tail_m = delete(m_list, idx)
    
    idx = where(no_tail_m < min_m)
    no_negative_dt = delete(no_tail_dt,idx )
    no_negative_m = delete(no_tail_m, idx)

    lm2 = sqrt(no_negative_m)

    
    x1 = lm2
    x2 = no_negative_dt
    
    #x = array([x1, x2])
    #x = x.transpose()
    '''
    gmm1_params = do_gmm(x1, 2, 'sqrt m')
    gmm2_params = do_gmm(x2, 2, 'dt')
    '''

    #means,variances,weights
    
    #low accel population, high accel population
    gmm1_params = [ 27.034,  71.619], [127.459,  1081.686],[ 0.749 ,  0.251]
    
    #long dt population, short dt population
    gmm2_params = [ 24.649,   2.421],  [706.153,3.18 ], [0.336,0.664]




    
    MIN_LOG_PROB = log(0.001)
    
    for key in d.keys():
        x = d[key]['pill']
        
        t = x[0]
        n = len(x[0])
        dt = diff(x[0])/60.0
        m = x[1]
        
        dt[where(dt > max_dt)] = 0.0

        m2 = sqrt(m)
        dt_evals = evaluate_log_likelihood(gmm2_params, dt)
        m_evals = evaluate_log_likelihood(gmm1_params, m2)
        
        
        log_probs = array([0, MIN_LOG_PROB])
        trajectory = zeros((n, 2))
        trajectory[0] = log_probs.copy()
        
        #conditional probabilities
        #sleep state0 = not sleep, state1 = sleep
        prob_short_dt_given_sleeps = array([0.6, 0.4]) #these do not have to add to 1.0
        prob_long_dt_given_sleeps = array([0.1, 0.9])
        prob_disturbance_given_sleeps = array([0.8,  0.2])
        
        EVENT_LOGLIK_THRESHOLD = 3.0
        
        for idata in xrange(n-1):
            t0 = t[idata]
            tf = t[idata+1]
            time_since_last_in_minutes = (tf - t0) / 60.0 
            if time_since_last_in_minutes > max_dt:
                #just reset probs for now
                log_probs[0] = log(0.95)
                log_probs[1] = log(0.05)
                
            if m[idata + 1] >= min_m:
                
                ldt = array([dt_evals[0][idata], dt_evals[1][idata]])
                lm = array([m_evals[0][idata + 1], m_evals[1][idata + 1]])
    
                
                log_lik_ratio_dt = ldt[0] - ldt[1]
                log_lik_ratio_m = lm[0] - lm[1]
                
                if log_lik_ratio_dt < -EVENT_LOGLIK_THRESHOLD:
                    log_probs += log(prob_short_dt_given_sleeps)
                    
                if log_lik_ratio_dt > EVENT_LOGLIK_THRESHOLD:
                    log_probs += log(prob_long_dt_given_sleeps)
                    
                if log_lik_ratio_m < -EVENT_LOGLIK_THRESHOLD:
                    log_probs += log(prob_disturbance_given_sleeps)
                
               
                
                #normalize
                log_probs -= amax(log_probs)
                
                #enforce minimum
                log_probs[where(log_probs < MIN_LOG_PROB)] = MIN_LOG_PROB
                
            
            p = exp(log_probs)
            p = p / sum(p)
            
            #print probs
            trajectory[idata+1] = p
            
        t2 = array(t).copy()
        t2 = t2 - t2[0]
        t2 /= 86400
        print (len(t), len(trajectory[:, 0]))
        print(len(t), len(m))
        plot(t2, trajectory[:, 1]*100, 'k', t2, sqrt(m), '.')
        title(key)
        show()
            
            
            
            
            
    
    #expect 3 distrubtions -- 
    #low dt, low energy
    #med to high dt, low to medium energy
    #any dt, high energy
    
  
  
    

 
