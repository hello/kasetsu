#!/usr/bin/python
import datetime
import calendar
import requests
import copy
import csv
import sys


num_days = 2
start_date_string = '2015-05-16'


k_endpoint = 'v1/datascience/timelinelog/'
k_account_endpoint = 'v1/datascience/activeusers'
#k_url = 'http://localhost:9997/v1/datascience/matchedfeedback/'
k_server = 'https://research-api-benjo.hello.is/'
#k_server = 'http://ec2-52-1-32-223.compute-1.amazonaws.com/'

k_url = k_server + k_endpoint
k_account_url = k_server + k_account_endpoint

k_magic_auth = '7.e0aa1ca0289449f5b3b3c257da9523ec'
#k_magic_auth = '2.26d34270933b4d5e88e513b0805a0644'

k_headers = {'Authorization' : 'Bearer %s' % k_magic_auth}


def get_datestr_as_timestamp(datestr):
    mydate = datetime.datetime.strptime(datestr, '%Y-%m-%d')
    return calendar.timegm(mydate.utctimetuple())*1000

def get_time_as_string(timestamp,offset):
    t = datetime.datetime.utcfromtimestamp(( offset + timestamp)/1000)
    return t.strftime('%Y-%m-%d %H:%M:%S')

def get_time_as_date(timestamp,offset):
    t = datetime.datetime.utcfromtimestamp(( offset + timestamp)/1000)
    return t.strftime('%Y-%m-%d')




k_params = {'from_ts_utc' : get_datestr_as_timestamp(start_date_string), 
            'num_days' : num_days, 
}

def csv_to_accounts(filename):
    account_ids = []
    with open(filename, 'rb') as csvfile:
        reader = csv.DictReader(csvfile)
        header = reader.next()

        for row in reader:
            account_ids.append(int(row['id']))
    
    return account_ids


def pull_data(accounts):
    headers = {'Authorization' : 'Bearer %s' % k_magic_auth}

    logs = []
    
    for account_id in accounts:
        params = copy.deepcopy(k_params)
        params['account_id'] = account_id
        
        response = requests.get(k_url,params=params,headers=headers)
            
        if not response.ok:
            print 'fail with %d on account %s ' % (response.status_code,str(account_id))
            continue
            
        data = response.json()
        
        #append account_id
        for item in data:
            item['account_id'] = account_id
        
        logs.extend(data)
        
    return logs

def pull_account_ids():
    headers = {'Authorization' : 'Bearer %s' % k_magic_auth}

    ids = []

    params = copy.deepcopy(k_params)

    response = requests.get(k_account_url,params=params,headers=headers)

    if not response.ok:           
        print 'fail with %d on account %s ' % (response.status_code,str(account_id))
    else:
        ids = response.json()


    return ids

       
def process_data(logs):
    for log in logs:
        log['created_date'] = get_time_as_date(log['created_date'], 0) 
        log['target_date'] = get_time_as_date(log['target_date'], 0) 
        
def logs_to_csv(logs, filename):
    numrows = 0
    with open(filename, 'w') as csvfile:
        fieldnames = ['account_id','algorithm','version','created_date', 'target_date']
        
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        writer.writeheader()
        
        for log in logs:
            writer.writerow(log)
            numrows += 1
            
    print "wrote %d rows" % numrows

if __name__ == '__main__':
    if len(sys.argv) > 1:
        input_filename = sys.argv[1]
        accounts = csv_to_accounts(input_filename)
    else:
        accounts = pull_account_ids()
        print "found %d accounts" % (len(accounts))
        filename = "%s--%d.csv" % (start_date_string,num_days)
        f = open(filename,'w')
        f.write('id\n')
        for acc in accounts:
            f.write(str(acc) + '\n')
        
        f.close()
        
    logs = pull_data(accounts)
    
    process_data(logs)
    logs_to_csv(logs, 'logs.csv')

