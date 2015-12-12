#!/usr/bin/python

import sys
import csv
import datetime
import calendar
dt_threshold = -60
event_map = {'IN_BED' : '11', 'SLEEP' : '12' , 'OUT_OF_BED' : '13' , 'WAKE_UP' : '14' }
event_types_str = ['WAKE_UP','OUT_OF_BED']


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

def main():
    event_types = [event_map[event_type] for event_type in event_types_str]

    events,count = get_events(sys.argv[1])
    found_events_count = 0
    events_we_care_about = []
    for event in events:
        if event['event_type'] in event_types:
            if event['dt'] < dt_threshold: 
                events_we_care_about.append(event)
                found_events_count += 1

    print 'found ',found_events_count,' out of ',count


    user_map = {}
    for event in events_we_care_about:
        account_id = event['account_id']

        if not user_map.has_key(account_id):
            user_map[account_id] = 1
        else:
            user_map[account_id] = user_map[account_id]  + 1

    user_count_list = []
    for key in user_map:
        user_count_list.append((key,user_map[key]))

    user_count_list.sort(key=lambda tup: tup[1])    
                
    with open('counts.csv','w') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=['account_id','count'])
        writer.writeheader()
        for item in user_count_list:
            mydict = {'account_id' : item[0], 'count' : item[1]}
            writer.writerow(mydict)
    
    with open(sys.argv[2],'w') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=events_we_care_about[0].keys())
        writer.writeheader()
        for event in events_we_care_about:
            writer.writerow(event)

            

if __name__ == '__main__':
    if len(sys.argv) <= 1:
        print 'requires two arguments, 1) input file  2) output file'
        sys.exit(0)

    main()


                                

                                
