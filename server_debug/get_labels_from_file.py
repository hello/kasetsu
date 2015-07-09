#!/usr/bin/python
import csv
import sys
import random
import copy
import numpy

rows_by_id_filename = 'rows2.csv'

def bootstrap(x,frac,num_times):
    n = len(x)
    nf = int(frac * n)

    means = []

    for i in range(num_times):
        x2 = copy.deepcopy(x)
        random.shuffle(x2)
        x2 = x2[0:nf]
        means.append(numpy.mean(x2))

    return numpy.sqrt(numpy.var(means) * frac)
    
    

def process_labels(labels):
    model_dict = {}
    raw_dict = {}

    for label in labels:
        model = label['model']
        p = float(label['label'])
        statenumber = int(label['state'])
        
        if not model_dict.has_key(model):
            model_dict[model] = {}
            raw_dict[model] = {}

        if not model_dict[model].has_key(statenumber):
            model_dict[model][statenumber] = (p,0.0,1)
            raw_dict[model][statenumber] = [p]
            continue

        raw_dict[model][statenumber].append(p)
        
        q = model_dict[model][statenumber]

        p1 = q[0]
        var1 = q[1]
        n = q[2]

        nt = p1 * float(n)

        nt += p        
        n += 1
        
        p2 = nt / n

        var2 = var1 + p1*p1 - p2*p2 + (p*p - var1 - p1*p1) / float(n)
        
        model_dict[model][statenumber] = (p2,var2,n)
        
    return model_dict,raw_dict

def reduce_data_by_user(rows):
    mydict= {}

    #go through every row
    for row in rows:
        account_id = row['account_id']
        model = row['model']
        state = int(row['state'])
        label = int(row['label'])

        #create entries in dictionary as needed
        if not mydict.has_key(account_id):
            mydict[account_id] = {}

        if not mydict[account_id].has_key(model):
            mydict[account_id][model] = {}

        m = mydict[account_id][model]

        #count labels
        if not m.has_key(state):
            m[state] = (0,0)

        s = m[state]
        s2 = s
        
        if label == 0:
            s2 = (s[0] + 1,s[1])

        if label == 1:
            s2 = (s[0],s[1] + 1)

        m[state] = s2


    rows2 = []
    #go through dictionary
    for account_id in mydict:
        models = mydict[account_id]

        for model in models:
            m = models[model]
            
            for state in m:
                s = m[state]
                T = s[0] + s[1]
                if T > 0:
                    p = float(s[1]) / float(T)
                else:
                    p = 0.5
 
                rows2.append({'account_id' : account_id, 'model' : model, 'state' : state, 'label' : p})
                
    return rows2

def get_data(filename):
    f = open(filename,'r')
    reader = csv.DictReader(f)

    rows = []
    for row in reader:
        rows.append(row)        
        
    f.close()

    return rows

if __name__ == '__main__':
    rows = get_data(sys.argv[1])
   
    rows2 = reduce_data_by_user(rows)
    f = open(rows_by_id_filename,'w')
    writer = csv.DictWriter(f,['account_id','model','state','label'])
    writer.writeheader()
    for row in rows2:
        writer.writerow(row)

    f.close()

    d,raw = process_labels(rows2)

    print 'motion'
    print [d['motion'][key][0] for key in d['motion']]

    print 'light2'
    print [d['light2'][key][0] for key in d['light2']]

    print 'sound2'
    print [d['sound2'][key][0] for key in d['sound2']]


