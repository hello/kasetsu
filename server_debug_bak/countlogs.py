#!/usr/bin/python
import sys
import csv

algs_of_interest = ['wupang','hmm']

def logs_to_count_dict(filename):
    counts = {}
    accounts = {}
    
   
    with open(filename, 'rb') as csvfile:
        reader = csv.DictReader(csvfile)
        header = reader.next()

        for row in reader:
            
            
            alg = row['algorithm']
            acc = row['account_id']
            
            if alg not in algs_of_interest:
                continue
            
            if not counts.has_key(alg):
                counts[alg] = 0
                
            counts[alg] += 1
            
            '''
            if accounts.has_key(acc):
                if accounts[acc] != alg:
                    print 'account %s already had alg %s, but was given %s' % (acc, accounts[acc], alg)
            '''
                    
            accounts[acc] = alg
            
    
    alg_uniques = {}
    for acc in accounts:
        alg = accounts[acc]
        
        if not alg_uniques.has_key(alg):
            alg_uniques[alg] = 0
            
        alg_uniques[alg] += 1
        
    return counts, alg_uniques
    
    
if __name__ == '__main__':
    counts, alg_uniques = logs_to_count_dict(sys.argv[1])
    
    n = 0
    for key in counts:
        c = counts[key]
        n += c
    
    
    print ('\nnum days per alg')
    for key in counts:
        print key, counts[key], counts[key] / float(n)
    
    
    '''
    print('\nnum unique accounts per alg')
    
    for key in alg_uniques:
        print key, alg_uniques[key]
    '''
    
    
