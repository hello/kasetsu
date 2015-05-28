#!/usr/bin/python

import csv
import pylab 
from numpy import *
from tabulate import tabulate

filename = 'experiment_002_results_raw.csv'
logfile = 'output.csv'
min_num_samples = 10
success_threshold = 20 #minutes
realbad_threshold = 60 #minutes

normalize_by_frequency_of_user = True

alg_name_map = {'hmm' : 'HMM', 'wupang' : 'REGULAR'}

keys_of_interest = ['IN_BED',  'SLEEP', 'WAKE_UP', 'OUT_OF_BED']
alg_fractions = {'HMM' : 0.203, 'REGULAR' : 0.797}
    

def get_fraction_from_key(key):
    for alg in alg_fractions:
        if alg in key:
            return alg_fractions[alg]
            
    return None

def get_stats(key, data, counts_by_account):
    
    frac = get_fraction_from_key(key)
    
    if frac == None:
        return None
        
    rows = data[key]


    #get fail count, normalized by account id
    count = 0
    normalized_fail_count = 0.0
    x = []
    for row in rows:
        delta = float(row['delta'])
        account_id = row['account_id']
        x.append(delta)
        
        cts = counts_by_account[account_id]
        
        normalizer = 1.0;
        if normalize_by_frequency_of_user:
            normalizer = 1.0 / cts
        
        if (abs(delta) > success_threshold):
            normalized_fail_count += normalizer * 1.0 / frac
        
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
    mydict['num_normalized_fail'] = normalized_fail_count
    mydict['frac'] = frac
    
    return mydict


def dict_entry_to_list(key, entry):
    return [key, entry['frac'], entry['num_fail'],  entry['median'], entry['num_samples']]

def get_valid_accounts():
    accounts = []
    with open(logfile, 'rb') as csvfile:
        reader = csv.DictReader(csvfile)
        
        for row in reader:
            acc = row['account_id']
            
            accounts.append(int(acc))
            
    return accounts

if __name__ == '__main__':
    counts_by_account = {}
    data_by_alg = {}
    
    accounts = get_valid_accounts()
    bad_accounts = {}
    with open(filename, 'rb') as csvfile:
        reader = csv.DictReader(csvfile)
        
        for row in reader:
            et = row['event_type']
            alg = row['algorithm']
            user = row['account_id']
            
            #if int(user) not in accounts:
            #    bad_accounts[user] = 1
            #    continue
            
            if alg not in alg_name_map.keys():
                continue
            else:
                alg = alg_name_map[alg]
                
            if et not in keys_of_interest:
                continue
            
            row['algorithm'] = alg
            
            key = alg + '_' + et
            
            
            if (not data_by_alg.has_key(key)):
                data_by_alg[key] = []
                
            if (not counts_by_account.has_key(user)):
                counts_by_account[user] = 0
                
            data_by_alg[key].append(row)
            counts_by_account[user] += 1
    
    #get sorted list of accounts
    '''
    sorted_account_ids_by_count = sorted(counts_by_account.items(), key=lambda x: x[1])
    end_idx = int(len(sorted_account_ids_by_count) * 0.9)
    sorted_account_ids_by_count = sorted_account_ids_by_count[0:end_idx]
    
    valid_accounts = [s[0] for s in sorted_account_ids_by_count]
    print valid_accounts
    '''
        
    print bad_accounts.keys()

    results = {}
    for key in data_by_alg.keys():
        stats = get_stats(key, data_by_alg, counts_by_account)
        
        if stats == None:
            continue
        
        if stats['num_samples'] < min_num_samples:
            continue
        
        results[key] = stats
        
    
    keys = results.keys()
    keys.sort()
    
    mylist = []
    headers = ['alg and type','fraction of test','num fails','median error', 'num feedbacks received']
    for key in keys:
        mylist.append(dict_entry_to_list(key, results[key]))
    
    print ('\n\n\n\n\n\n\n')
    print ('fail > %d min, positive error = early prediction' % (success_threshold))
    print('\n')
    print tabulate(mylist, headers=headers)
    print ('\n\n\n\n\n\n\n')
    
