#!/usr/bin/python
import time
import psycopg2
import os
import datetime
import time
import requests
import logging as LOGGER

k_devices = [
'1005F47CFB40C4E9',
'04837B2F8DAD9D71',
'75DC4844E684EF07',
'5EE8ADB08573A954',
'4B42408AE6898D43',
'03185E594B273B3C',
'D8EF10B09CCDCD18',
'F931EB0F5752FE5A',
'E9D2498F2258FBEA',
'C8DAAC353AEFA4A9',
'E0A14B6AED2DA0FF',
'87AAADAD23D98ADE',
'AB9CB428A7837C86',
'D78BD9241BAE0E56']

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

def post_startup_message(found_devices,devices):
    r = requests.post(k_slack_url, json={'text': 'SCRIPT STARTUP\n Looking for these devices: \n%s \n\nAlready have these devices:\n%s' % ('\n'.join(devices),'\n'.join(found_devices))})

if __name__=='__main__':
    LOGGER.basicConfig(level=LOGGER.INFO)
    existing_accs = set()
    acc_device_map = {}

    is_first = True

    while(True):
        res = do_query()

        for a in res:
            acc_device_map[str(a[0])] = a[1]

        accs = set([ '%d' % (a[0]) for a in res])
        new_accs = accs.difference(existing_accs)
        existing_accs.update(new_accs)
      
        new_acc_pairs = ['account=%s, device=%s' % (a,acc_device_map[a]) for a in new_accs]

        if is_first:
            post_startup_message(new_acc_pairs,k_devices)
            is_first = False
        elif len(new_accs) > 0:
            post_new_accounts(new_acc_pairs)

        time.sleep(60)


