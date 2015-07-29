#!/usr/bin/python
import requests
import os
import sys
import csv
import copy

k_uri = 'https://research-api-benjo.hello.is/v1/prediction/partnerfilter_predictions/{}/{}/'
k_magic_auth = os.environ['RESEARCH_TOKEN']
k_headers = {'Authorization' : 'Bearer %s' % k_magic_auth}

k_target_file = 'partnerfeedbacks.csv'
#k_target_file = 'p.csv'

k_output_file = 'part_pred_err.csv'

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
    
        event_type = row['event_type']
        if event_type == 'IN_BED' or event_type == 'OUT_OF_BED':
            rows.append(row)

    f.close()

    return rows

if __name__ == '__main__':
    rows = get_in_out_of_bed(k_target_file)
    count = 0

    f = open(k_output_file,'w')
    writer = csv.DictWriter(f,fieldnames=['account_id','query_date','event_type','prediction_error','orig_error'],extrasaction='ignore')
    writer.writeheader()
                            
    for row in rows:
        query_date = row['query_date']
        account_id = row['account_id']
        event_type = row['event_type']
        print 'querying %s for account %s' % (query_date,account_id)
        data = pull_data(query_date,account_id)

        if data == None:
            continue


        if len(data) > 1:
            print 'ERRROR skipping because more than one segment found for account %s on %s' % (account_id,query_date)

        result = data[0]
        feedback_time = int(row['new_time_utc'])
        orig_time = int(row['old_time_utc'])

        predicted_time_in_bed = int(result['start_time_utc'])
        predicted_time_out_of_bed = int(result['end_time_utc'])

        diff = None
        
        if event_type == 'OUT_OF_BED':
            diff = (feedback_time - predicted_time_out_of_bed) / 60000
        elif event_type == 'IN_BED':
            diff = (feedback_time - predicted_time_in_bed) / 60000

        orig_error = (feedback_time - orig_time) / 60000

        if diff != None:
            row2 = copy.deepcopy(row)
            row2['prediction_error'] = diff
            row2['orig_error'] = orig_error

            writer.writerow(row2)

        
  

    f.close()
