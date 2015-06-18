#!/usr/bin/python

import requests
import os
import sys


k_uri = 'https://research-api-benjo.hello.is/v1/datascience/partneraccountswithfeedback/{}'
k_magic_auth = os.environ['RESEARCH_TOKEN']
k_num_days = 3
k_params = {'num_days' : k_num_days}

headers = {'Authorization' : 'Bearer %s' % k_magic_auth}

def pull_data(datestring):
    url = k_uri.format(datestring)

    response = requests.get(url,params=k_params,headers = headers)

    if not response.ok:
        print 'fail with %d on %s ' % (response.status_code,datestring)
        return


    print response.json()


if __name__ == '__main__':
    pull_data(sys.argv[1])

    
