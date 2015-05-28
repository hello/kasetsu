#!/usr/bin/python
import datetime
import calendar
import requests
import copy
import csv

num_days = 2
start_date_string = '2015-05-16'

k_endpoint = 'v1/datascience/matchedfeedback/'
#k_url = 'http://localhost:9997/v1/datascience/matchedfeedback/'
#k_server = 'https://research-api-benjo.hello.is/'
k_server = 'http://ec2-52-1-32-223.compute-1.amazonaws.com/'
k_url = k_server + k_endpoint

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

def pull_data():
    responses = []
    
    params = copy.deepcopy(k_params)
    headers = {'Authorization' : 'Bearer %s' % k_magic_auth}
    
    response = requests.get(k_url,params=params,headers=headers)
        
    if not response.ok:
        print 'fail with %d on %s ' % (response.status_code,'foo')
        return []

    data = response.json()
        
    return data
       
def process_data(data):
    for event in data:
        event['delta'] = event['delta'] / 60000
        event['date'] = get_time_as_date(event['date'], 0)
        
def data_to_csv(data, filename):
    numrows = 0
    with open(filename, 'w') as csvfile:
        fieldnames = ['date','event_type','account_id', 'algorithm', 'delta', 'version']
        
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        writer.writeheader()
        
        for event in data:
            writer.writerow(event)
            numrows += 1
            
    print "wrote %d rows" % numrows

if __name__ == '__main__':
    data = pull_data()
    process_data(data)
    data_to_csv(data, 'output.csv')

