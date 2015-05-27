#!/usr/bin/python


import csv
import argparse
import datetime
import calendar
from tabulate import tabulate

k_type_map = {'IN_BED' : 'PRED_IN_BED', 'SLEEP' : 'PRED_SLEEP', 'WAKE_UP' : 'PRED_WAKE_UP', 'OUT_OF_BED' : 'PRED_OUT_OF_BED'}

k_fail_threshold = 20 #minutes

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

def accumulate_stats_by_account(account_dict):
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


        f += failcount
        c += totalcount
        
        mydict[key] = {'total' : totalcount,'fail' : failcount, 'success' : totalcount - failcount}

    mydict['TOTALS'] = {'total' : c,'fail' : f, 'success' : c - f}

    return mydict
                

def flatten_by_account(entries):

    mydict = {}

    for entry in entries:
        account_id = entry['account_id']

        if not mydict.has_key(account_id):
            mydict[account_id] = []

        for key in k_type_map:
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

    args = parser.parse_args()

    entries = []
    with open(args.input,'rb') as csvfile:
        reader = csv.DictReader(csvfile)

        for row in reader:
            entry = get_row_as_deltas(row)
            entries.append(entry)

    byaccount = flatten_by_account(entries)
    stats = accumulate_stats_by_account(byaccount)

    for key in byaccount:
        print '\n\n\n'
        print key
        print tabulate(byaccount[key],['date','event type','delta'],tablefmt='simple')

    statsrows = []
    for key in byaccount:
        newrow = []
        newrow.append(key)
        newrow.append(stats[key]['success'])
        newrow.append(stats[key]['total'])
        newrow.append(float(stats[key]['success']) / float(stats[key]['total']))                     

        statsrows.append(newrow)

    key = 'TOTALS'
    newrow = []
    newrow.append(key)
    newrow.append(stats[key]['success'])
    newrow.append(stats[key]['total'])
    newrow.append(float(stats[key]['success']) / float(stats[key]['total']))                  

    statsrows.append(newrow)


    print tabulate(statsrows,['account_id','successes','total counts','success fraction'],tablefmt = 'simple')
        


    
    
