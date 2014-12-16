#!/usr/bin/python

def join_by_account_id(mydata, min_count_pill_data = 250):
    
    pilldata = mydata['pill']
    sensedata = mydata['sense']
    
    #filter out accounts with two or more senses and two or more pills
    #and accounts that don't have pills
    goodkeys = []
    for key in sensedata:
        if not pilldata.has_key(key):
            continue
            
        if len(pilldata[key]) > 1:
            continue
            
        if len(sensedata[key]) > 1:
            continue
            
        goodkeys.append(key)
        
        
    joined = {}
    
    for key in goodkeys:
        joined[key] = {}
        
        joined[key]['pill'] = pilldata[key][pilldata[key].keys()[0]]

        joined[key]['sense'] = sensedata[key][sensedata[key].keys()[0]]

        min_count_pill_data
    
    goodkeys = [key for key in joined if len(joined[key]['pill'][0]) > min_count_pill_data]
    
    filtered_data = {}
    for key in goodkeys:
        filtered_data[key] = joined[key]
        
    return filtered_data
        
