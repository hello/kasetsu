#!/usr/bin/python
import utils
import sys
import csv

def main():
    events,count = utils.get_events(sys.argv[1])

    recognized_events = utils.event_map_reversed.keys()


    new_events = []
    for event in events:
     
        if event['event_type'] not in recognized_events:
            continue

        event_type = utils.event_map_reversed[event['event_type']]
        account_id = event['account_id']
        
        ts = utils.get_feedback_date_time_as_timestamp(event['date_of_night'],event['new_time'])

        new_event = {'account_id' : account_id, 'event_type' : event_type, 'ts_local_utc' : ts}
        
        new_events.append(new_event)


    with open(sys.argv[2], 'w') as csvfile:
        fieldnames = ['account_id', 'event_type','ts_local_utc']
        
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        writer.writeheader()

        for event in new_events:
            writer.writerow(event)


if __name__ == '__main__':
    main()
        
