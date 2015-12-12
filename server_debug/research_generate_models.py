#!/usr/bin/python

import sys
import datetime
import requests
import numpy as np
import time
import json
import os
from multiprocessing import Pool
import csv
import online_hmm_pb2
import base64
import argparse


k_uri = 'https://research-api-benjo.hello.is/v1/prediction/generate_models/{}/{}/{}'
k_magic_auth = os.environ['RESEARCH_TOKEN']
k_headers = {'Authorization' : 'Bearer %s' % k_magic_auth}
k_pool_size = 4

def get_user_list(f):
    csvfile = csv.reader(f)
    user_list = []
    for row in csvfile:
        user_list.append(int(row[0]))

    return user_list

def get_time_as_string(timestamp,offset):
    t = datetime.datetime.utcfromtimestamp(( offset + timestamp)/1000)
    return t.strftime('%Y-%m-%d %H:%M:%S')

def pull_data(mytuple):
    start_date_string,account_id,num_days = mytuple

    #print 'generating for account_id=%d,num_days=%d,date=%d' % (account_id,num_days,start_date_string)
    
    url = k_uri.format(account_id,start_date_string,num_days)
    print url
    response = requests.get(url,params={},headers = k_headers)
    
    if not response.ok:
        print 'fail with %d on %s ' % (response.status_code,start_date_string)
        return None
    
    data = response.json()

    if isinstance(data,dict) and data.has_key('code') and int(data['code']) == 204:
        print data['message']
        return None                  

    if not data.has_key('model_protobuf'):
        return None

    return data
   
         
            

def join_protobufs_and_write_to_file(datas,outfilename):

    joined_models = online_hmm_pb2.AlphabetHmmUserModel()
    
    for item in datas:
        
        if item == None:
            continue
        
        base = str(item['account_id'])
        
        bindata = base64.b64decode(item['model_protobuf'])

        protobuf = online_hmm_pb2.AlphabetHmmUserModel()
        protobuf.ParseFromString(bindata)

        for model in protobuf.models:
            model.id = base + '-' + model.id
            print model.id

        joined_models.models.extend(protobuf.models)


    f = open(outfilename,'w')
    f.write(joined_models.SerializeToString())
    f.close()


                
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-o','--outfile',required=True)
    parser.add_argument('--date',required=True)
    parser.add_argument('-n','--numdays',default=1,type=int)
    parser.add_argument('--partnerfilter',default=False,action='store_true')
    parser.add_argument('-u','--user',help='user id number')
    parser.add_argument('--userlistfile',help='file of user account ids')
    args = parser.parse_args()


    if args.user == None:
        if args.userlistfile == None:
            print 'must supply user list file or user'
            sys.exit(0)

        f = open(args.userlistfile)
        user_list = get_user_list(f)
        f.close()
    else:
        user_list = [int(args.user)]

    argslist = []

    for user in user_list:
        argslist.append((args.date,user,int(args.numdays)))


    pool = Pool(k_pool_size)

    protobufs = pool.map(pull_data,argslist)

    print 'writing to %s' % args.outfile
    join_protobufs_and_write_to_file(protobufs,args.outfile)

