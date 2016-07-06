#!/usr/bin/python
import psycopg2
import os
import datetime
import time
import json

event_types = [12,14]

def get_key(dt):
    return dt.isoformat()

def main():
    conn = psycopg2.connect("dbname='common' user='common' host='common-replica-1.cdawj8qazvva.us-east-1.rds.amazonaws.com' port=5432 password='hello-common'")
    conn2 = psycopg2.connect("dbname='sensors1' user='benjo' host='sensors2.cy7n0vzxfedi.us-east-1.redshift.amazonaws.com' port=5439 password='%s'" % (os.getenv('REDSHIFT_PW')))

    with open('query.str','r') as f:
        query_str = f.read()

    with open('query_total_count.sql','r') as f:
        query_total_str = f.read()
        

    cur2 = conn2.cursor()
    cur2.execute(query_total_str)

    total_counts = {}

    for record in cur2:
        dt = record[0]
        count = record[1]
        total_counts[get_key(dt)] = count

    cur = conn.cursor()

    all_count_dicts = []
    for event in event_types:
        count_dict = {}
        
        query = query_str.format(str(event))

        cur.execute(query)

        for record in cur:
            dt = record[0]
            count = record[1]
            count_dict[get_key(dt)] = count

        all_count_dicts.append(count_dict)

    rates = []
    for count_dict in all_count_dicts:
        rate_dict = {}
        
        for key in count_dict:
            
            if not total_counts.has_key(key):
                continue
            
            count = count_dict[key]
            total_count = total_counts[key]

            rate = float(count) / float(total_count)

            rate_dict[key] = rate

        rates.append(rate_dict)

    with open('rates.json','w') as f:
        json.dump(rates,f)

if __name__=='__main__':
    main()


