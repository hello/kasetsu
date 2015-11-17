#!/usr/bin/python

import sys
import csv
import datetime
import calendar
import numpy as np
import random
import copy
dt_threshold = 30
event_map = {'IN_BED' : '11', 'SLEEP' : '12' , 'OUT_OF_BED' : '13' , 'WAKE_UP' : '14' }
#event_types_str = ['SLEEP','IN_BED','WAKE_UP','OUT_OF_BED']
event_types_str = ['SLEEP','WAKE_UP']

min_feedbacks = 30
normies_max_median = 30
problems_min_median = 60

base_date = '1970-01-01'
def get_datestr_as_timestamp(datestr):
    mydate = datetime.datetime.strptime(datestr, '%Y-%m-%d %H:%M')
    ts = calendar.timegm(mydate.utctimetuple())
    return ts;

def subtract_times(ts2,ts1):
    t2str = base_date + ' ' + ts2
    t1str = base_date + ' ' + ts1

    t2 = get_datestr_as_timestamp(t2str)
    t1 = get_datestr_as_timestamp(t1str)

    dt = t2 - t1

    if dt > 86400 / 2:
        dt -= 86400

    if dt < -86400 / 2:
        dt += 86400

    dt /= 60
    return dt

def get_events(filename):
    count = 0
    events = []
    with open(filename) as csvfile:
        reader = csv.DictReader(csvfile,delimiter=',')
        
        for row in reader:
            dt = subtract_times(row['new_time'],row['old_time'])
            event = {'dt': dt,
                     'account_id' : row['account_id'],
                     'date_of_night' : row['date_of_night'],
                     'event_type' : row['event_type'],
                     'new_time' : row['new_time']}

            events.append(event)
            count += 1


    return events,count

#['dt', 'date_of_night', 'account_id', 'new_time', 'event_type']
class EventAggregator(object):
    def __init__(self,events):
        self.events = events


    def process(self):
        self.stats = self.compute_stats()
        
    def compute_stats(self):
        mydict = {}
        for event in self.events:
            acc = event['account_id']

            if not mydict.has_key(acc):
                mydict[acc] = []

            mydict[acc].append(abs(event['dt']))

        results = {}
        for key in mydict:
            median = np.median(mydict[key])
            count = len(mydict[key])
            stats = count,median

            results[key] = stats

        return results

    def find_accounts(self,min_count,min_median,max_median):
        accs = {}
        for key in self.stats:
            s = self.stats[key]

            if min_count != None and s[0] < min_count:
                continue

            if min_median != None and s[1] < min_median:
                continue

            if max_median != None and s[1] > max_median:
                continue

            accs[key] = s

        return accs
        
             
            
def randomize_and_split(mylist):
    randlist = copy.deepcopy(mylist)
    random.shuffle(randlist)
    N = len(randlist) / 2
    list1 = [randlist[i] for i in range(0,N)]
    list2 = [randlist[i] for i in range(N,len(randlist))]

    return list1,list2

def write_accounts_list(mylist,filename):
    print 'writing %s with %d items' % (filename,len(mylist))

    with open(filename,'w') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=['account_id'])
        writer.writeheader()
        for item in mylist:
            writedict = {'account_id' : item}
            writer.writerow(writedict)

def main():
    event_types = [event_map[event_type] for event_type in event_types_str]

    events,count = get_events(sys.argv[1])

    agg = EventAggregator(events)
    agg.process()

    accounts_for_normies = agg.find_accounts(min_feedbacks,None,normies_max_median)
    print len(accounts_for_normies)

    accounts_for_problems = agg.find_accounts(min_feedbacks,problems_min_median,None)
    print len(accounts_for_problems)

    intersection = set(accounts_for_normies.keys()).intersection(set(accounts_for_problems.keys()))

    if len(intersection) > 0:
        print 'ERROR: there was an intersection of normies and problem users'
        sys.exit(0)

    normiesA,normiesB = randomize_and_split(accounts_for_normies.keys())
    problemA,problemB = randomize_and_split(accounts_for_problems.keys())

    write_accounts_list(normiesA,'normiesA.csv') 
    write_accounts_list(normiesB,'normiesB.csv') 
    write_accounts_list(problemA,'problemA.csv') 
    write_accounts_list(problemB,'problemB.csv') 

            

if __name__ == '__main__':
    if len(sys.argv) <= 1:
        print 'requires input file'
        sys.exit(0)

    main()


                                

                                
