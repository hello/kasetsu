#!/usr/bin/python

import csv
import pylab 
from numpy import *
from tabulate import tabulate

filename = 'experiment_001_results_raw.csv'
min_num_samples = 10
success_threshold = 20 #minutes
realbad_threshold = 60 #minutes


keys_of_interest = ['IN_BED',  'SLEEP', 'WAKE_UP', 'OUT_OF_BED']
alg_fractions = {'hmm' : 0.3, 'wupang' : 0.7}

def get_fraction_from_key(key):
    for alg in alg_fractions:
        if alg in key:
            return alg_fractions[alg]
            
    return None

def get_stats(x, key):
    
    frac = get_fraction_from_key(key)

    if frac == None:
        return None
        
    x = array(x)
    mydict = {}
    
    
    
    N = float(x.shape[0])
    mx = mean(x) 
    sx = std(x)
    medx = median(x)
    numsuccess = x[where(abs(x) <= success_threshold)].shape[0]
    numfail = x[where(abs(x) > success_threshold)].shape[0]
    numrealbad = x[where(abs(x) <= realbad_threshold)].shape[0]
    psuccess = numsuccess / N
    pfail = 1.0 - psuccess;
    prealbad = numrealbad / N
    
    denom_success = psuccess * (1 - psuccess)
    denom_realbad = prealbad * (1 - prealbad)
    
    fisher_information_success = N / (denom_success)
    fisher_information_realbad = N / (denom_realbad)

    mydict['mean'] = mx
    mydict['median'] = medx
    mydict['stddev'] = sx
    mydict['num_samples'] = N
    mydict['success_ratio'] = psuccess
    mydict['realbad_ratio'] = prealbad
    mydict['num_fail'] = numfail
    mydict['success_confidence'] = 2 / sqrt(fisher_information_success) #2 sigma
    mydict['realbad_confidence'] = 2 / sqrt(fisher_information_realbad) #2 sigma
    mydict['num_normalized_fail'] = int(numfail / frac)
    mydict['frac'] = frac
    


    return mydict


def dict_entry_to_list(key, entry):
    return [key, entry['frac'], entry['num_normalized_fail'], entry['median'], entry['num_samples'], entry['success_ratio'], entry['success_confidence'], entry['realbad_ratio'], entry['realbad_confidence']]

distributions = {}



with open(filename, 'rb') as csvfile:
    reader = csv.DictReader(csvfile)
    
    for row in reader:
        et = row['event_type']
        alg = row['algorithm']
        key = alg + '_' + et
        if (not distributions.has_key(key)):
            distributions[key] = []
            
        distributions[key].append(-int(row['delta']))
        
results = {}
for key in distributions.keys():
    try:
        stats = get_stats(distributions[key], key)
        
        if stats == None:
            continue
        
        if stats['num_samples'] < min_num_samples:
            continue
        
        results[key] = stats
    except Exception:
        foo = 3

keys = results.keys()
keys.sort()

mylist = []
headers = ['alg and type','fraction of test','num normalized fails','median error','# samp','success fraction','confidence','utter fail fraction','confidence']
for key in keys:
    mylist.append(dict_entry_to_list(key, results[key]))

print ('\n\n\n\n\n\n\n')
print ('succes < %d min error, utter fail > %d min error, positive error = early prediction' % (success_threshold, realbad_threshold))
print tabulate(mylist, headers=headers)
print ('\n\n\n\n\n\n\n')

