#!/usr/bin/python
import requests
import os
import sys
import csv

k_uri = 'https://research-api-benjo.hello.is/v1/prediction/partnerfilter_predictions/{}/{}/'
k_magic_auth = os.environ['RESEARCH_TOKEN']
k_num_days = 3

k_headers = {'Authorization' : 'Bearer %s' % k_magic_auth}

k_target_file = 'partnerfeedbacks.csv'
#k_target_file = 'p.csv'

def pull_data(datestring,account_id):

    url = k_uri.format(account_id,datestring)

 
    response = requests.get(url,params=None,headers = k_headers)

    if not response.ok:
        print 'fail with %d on %s ' % (response.status_code,datestring)
        return None


    return response.json()


def get_in_out_of_bed(filename):
    f = open(filename,'r')

    reader = csv.DictReader(f)

    rows = []
    
    for row in reader:
        #account_id,query_date,event_type,new_time_utc,old_time_utc
        event_type = row['event_type']
        if event_type == 'IN_BED' or event_type == 'OUT_OF_BED':
            rows.append(row)

    f.close()

    return rows

if __name__ == '__main__':
    rows = get_in_out_of_bed(k_target_file)
    count = 0
    for row in rows:
        query_date = row['query_date']
        account_id = row['account_id']

        print 'querying %s for account %s' % (query_date,account_id)
        data = pull_data(query_date,account_id)

        if data == None:
            continue


        if len(data) > 1:
            print 'ERRROR skipping because more than one segment found for account %s on %s' % (account_id,query_date)

        result = data[0]
        feedback_time = int(row['new_time_utc'])
        predicted_time = int(result['start_time_utc'])

        print (feedback_time - predicted_time) / 60000
        
        count += 1

        if count > 10:
            break
        
