#!/usr/bin/python


import csv
import argparse
import datetime
import calendar
from tabulate import tabulate
import math
#k_type_map = {'IN_BED' : 'PRED_IN_BED', 'SLEEP' : 'PRED_SLEEP', 'WAKE_UP' : 'PRED_WAKE_UP', 'OUT_OF_BED' : 'PRED_OUT_OF_BED'}
k_type_map = {'LABEL_IN_BED' : 'PRED_IN_BED', 'LABEL_SLEEP' : 'PRED_SLEEP', 'LABEL_WAKE_UP' : 'PRED_WAKE_UP', 'LABEL_OUT_OF_BED' : 'PRED_OUT_OF_BED'}
k_fail_threshold = 20 #minutes
k_bootstrap_fraction = 0.2

def get_datestr_as_timestamp(datestr):
    mydate = datetime.datetime.strptime(datestr, '%Y-%m-%d')
    ts = calendar.timegm(mydate.utctimetuple())
    return ts;

def get_time_in_seconds_from_datetime(dt):
    return calendar.timegm(dt.utctimetuple())

def get_delta_time_from_HH_MM(timestr):
    hhmm = timestr.split(':')
    hour = int(hhmm[0])
    minute = int(hhmm[1])

    if hour < 16:
        hour += 24

    return datetime.timedelta(hours=hour,minutes=minute)

def accumulate_stats_by_account(account_dict,normalize):
    mydict = {}

    c = 0
    f = 0
    for key in account_dict:
        failcount = 0
        totalcount = 0
        
        table = account_dict[key]
        for item in table:
            totalcount += 1
            if abs(item[2]) > k_fail_threshold:
                failcount += 1


        
        if normalize:
            failcount /= float(totalcount)
            totalcount = 1.0

        f += failcount
        c += totalcount
        
        mydict[key] = {'total' : totalcount,'fail' : failcount, 'success' : totalcount - failcount}

    mydict['TOTALS'] = {'total' : c,'fail' : f, 'success' : c - f}

    return mydict



                

def flatten_by_account(entries,eventkey = None,normalize=False):

    mydict = {}

    for entry in entries:
        account_id = entry['account_id']

        if not mydict.has_key(account_id):
            mydict[account_id] = []

        event_list = k_type_map.keys()
        if eventkey != None:
            event_list = [eventkey]
            
        for key in event_list:
            if not entry.has_key(key):
                continue
            
            delta = entry[key]
            
            mydict[account_id].append([entry['date'],key,delta])


    for key in mydict:
        mydict[key] = sorted(mydict[key], key=lambda x:x[0])
        
            
    return mydict

def get_row_as_deltas(row):
    datestr = row['date']

    mydate = datetime.datetime.strptime(datestr, '%Y-%m-%d')

    mydict = {}
    for key in k_type_map:
        pred = row[k_type_map[key]]
        actual = row[key]

        #skip if no label
        if len(actual) < 3:
            continue

        if len(pred) >= 3:
            
            predicted_time = mydate + get_delta_time_from_HH_MM(pred)
            actual_time = mydate + get_delta_time_from_HH_MM(actual)

            delta = get_time_in_seconds_from_datetime(actual_time) - get_time_in_seconds_from_datetime(predicted_time)
            delta /= 60 #convert from seconds to minutes
        else:
            delta = float("inf")

        mydict[key] = delta
        mydict['account_id'] = row['account_id']
        mydict['date'] = row['date']
        
    return mydict
        

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-i','--input', help = 'input label file',required=True)
    parser.add_argument('--event',help = 'optional event type to filter on')
    parser.add_argument('-v','--verbose',help = 'display each event for each user',default=False,action='store_true')
    parser.add_argument('--threshold',help = 'threshold in minutes for success',default=k_fail_threshold,type=int)
    parser.add_argument('--normalize',help = 'normalize by 1 / # contributions from an individual',default=False,action='store_true')
    parser.add_argument('--output',help='output vector of deltas')
    args = parser.parse_args()


    k_fail_threshold = args.threshold

    entries = []
    with open(args.input,'rb') as csvfile:
        reader = csv.DictReader(csvfile)

        for row in reader:
            entry = get_row_as_deltas(row)
            entries.append(entry)

    byaccount = flatten_by_account(entries,args.event)
    
    if args.output != None and args.event != None:
        vec = []
        for key in byaccount:
            items = byaccount[key]
            for item in items:
                vec.append(item[2])

        with open(args.output,'wb') as csvfile:
            writer = csv.writer(csvfile,delimiter=',')
            for item in vec:
                if math.isinf(item):
                    continue 
                writer.writerow([item])
        
             
    stats = accumulate_stats_by_account(byaccount,args.normalize)

    if args.verbose:
        for key in byaccount:
            print '\n\n\n'
            print key
            print tabulate(byaccount[key],['date','event type','delta'],tablefmt='simple')


    if args.event != None:
        print '\n\nFILTERING ON EVENT TYPE = %s' % (args.event)
    else:
        print '\n\nPROCESSING ALL EVENT TYPES'

    statsrows = []
    for key in byaccount:
        newrow = []
        newrow.append(key)
        newrow.append(stats[key]['success'])
        newrow.append(stats[key]['total'])
        total = float(stats[key]['total'])

        if total <= 0:
            total = 1
        
        newrow.append(float(stats[key]['success']) / total)                     

        statsrows.append(newrow)

    key = 'TOTALS'
    newrow = []
    newrow.append(key)
    newrow.append(stats[key]['success'])
    newrow.append(stats[key]['total'])
    total = float(stats[key]['total'])
    if total <= 0:
        total = 1
    newrow.append(float(stats[key]['success']) / total)                  

    statsrows.append(newrow)


    print tabulate(statsrows,['account_id','successes','total counts','success fraction'],tablefmt = 'simple')
        


    
    
