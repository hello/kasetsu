#!/usr/bin/python
import requests
import sys
import argparse
import calendar
import datetime
import json

k_url = 'http://127.0.0.1:9999/v2/timeline/{}/events/{}/{}'
k_auth = '4.749bff8cb91847119385bf9c85abb131' #some random user in local database




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

    args = parser.parse_args()

    oldtimestr = args.date + ' ' + args.updatetime
    oldtimestamp = get_datestr_as_timestamp(oldtimestr)

    timeline_event = {'new_event_time' : args.updatetime}


    url = k_url.format(args.date,args.type,oldtimestamp)

    print url

    headers = {'Authorization' : 'Bearer %s' % k_auth , 'Content-Type': 'application/json'}
    response = requests.patch(url,json.dumps(timeline_event),headers = headers)

if __name__ == '__main__':
    main()
