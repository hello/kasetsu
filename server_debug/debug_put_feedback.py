#!/usr/bin/python
import requests
import sys
import argparse
import calendar
import datetime
import json

print 'GOT_IN_BED, FELL_ASLEEP, WOKE_UP, GOT_OUT_OF_BED'
k_url = 'http://127.0.0.1:9999/v2/timeline/{}/events/{}/{}'
#k_auth = '2.26d34270933b4d5e88e513b0805a0644' #some random user in local database
k_auth = '4.749bff8cb91847119385bf9c85abb131'



def get_datestr_as_timestamp(datestr):
    mydate = datetime.datetime.strptime(datestr, '%Y-%m-%d %H:%M')
    ts = calendar.timegm(mydate.utctimetuple())
    print ts

    return 1000 * ts;

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--date','-d',required=True)
    parser.add_argument('--type','-t',required=True)
    parser.add_argument('--updatetime','-u',required=True)
    parser.add_argument('--timezone','-z',type=int,required=True,help='hour offset of timzeone (i.e. -7,-8, 1)')
    args = parser.parse_args()
    time_cutoff_string = args.date + ' 20:00'
    time_cutoff = get_datestr_as_timestamp(time_cutoff_string)

    print 'timezone is ',args.timezone

    oldtimestr = args.date + ' ' + args.updatetime
    oldtimestamp = get_datestr_as_timestamp(oldtimestr)

    if oldtimestamp < time_cutoff:
        oldtimestamp += 86400000

    oldtimestamp -= args.timezone * 3600000

    timeline_event = {'new_event_time' : args.updatetime}


    url = k_url.format(args.date,args.type,oldtimestamp)

#    print url

    headers = {'Authorization' : 'Bearer %s' % k_auth , 'Content-Type': 'application/json'}
#    print url
#    print timeline_event
    response = requests.patch(url,json.dumps(timeline_event),headers = headers)

if __name__ == '__main__':
    main()
