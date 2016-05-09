#!/usr/bin/python
import time
import psycopg2
import os
import datetime
import time
import requests
import logging as LOGGER
k_devices = ['1005F47CFB40C4E9','04837B2F8DAD9D71','75DC4844E684EF07','5EE8ADB08573A954','4B42408AE6898D43','184D09D04FA9CCAA']
k_slack_url = 'https://hooks.slack.com/services/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'
k_db_url = 'common-replica-1.cdawj8qazvva.us-east-1.rds.amazonaws.com'
k_db_username = 'common'
k_db_pw = 'hello-common'
k_db = 'common'

k_query_str = 'SELECT account_id,device_id FROM account_device_map WHERE device_id IN ({0});'

def do_query():
    query = get_query(k_query_str,k_devices)
    conn = psycopg2.connect("dbname='%s' user='%s' host='%s' port=5432 password='%s'" % (k_db,k_db_username,k_db_url,k_db_pw))
    cur = conn.cursor()
    tic1 = time.time()
    cur.execute(query)
    tic2 = time.time()

    items = []
    for item in cur:
        items.append(item)

    conn.close()
    LOGGER.info('dt=%s num_items=%d' % (tic2-tic1,len(items)))
    return items
    
def get_query(querystr,devices):
    stringified_devices = [ "'%s'" % d for d in devices]
    device_str = ','.join(stringified_devices)
    return k_query_str.format(device_str)
    
def post_new_accounts(accounts):
    r = requests.post(k_slack_url, json={'text': '@benjo new accounts found\n%s' % ('\n'.join(accounts)) })

def post_startup_message(devices):
    r = requests.post(k_slack_url, json={'text': 'SCRIPT STARTUP\n Looking for these guys: \n %s' % ('\n'.join(devices))})

if __name__=='__main__':
    LOGGING.basicConfig(level=logging.DEBUG)
    existing_accs = set()
    acc_device_map = {}
    post_startup_message(k_devices)
    while(True):
        res = do_query()

        for a in res:
            acc_device_map[str(a[0])] = a[1]

        accs = set([ '%d' % (a[0]) for a in res])
        new_accs = accs.difference(existing_accs)
        existing_accs.update(new_accs)
      
        new_acc_pairs = ['account=%s, device=%s' % (a,acc_device_map[a]) for a in new_accs]

        if len(new_accs) > 0:
            post_new_accounts(new_acc_pairs)

        
        time.sleep(60)


