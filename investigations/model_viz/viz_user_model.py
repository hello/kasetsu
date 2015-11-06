#!/usr/bin/python
import boto
from boto.dynamodb2.table import Table
from boto.dynamodb2.items import Item
from boto.dynamodb2 import layer1
from boto.dynamodb2.layer1 import DynamoDBConnection
from boto.dynamodb2.exceptions import *
import os 
import sys
import argparse
import base64
from boto.dynamodb.types import Binary
from boto.dynamodb.types import Dynamizer
import calendar
import datetime
from time import strftime
import online_hmm_pb2
from matplotlib.pyplot import *
import numpy as np

k_env_name_for_amazon_id = 'AWS_ACCESS_KEY_ID'
k_env_name_for_amazon_secret_key = 'AWS_SECRET_KEY'
k_region = 'us-east-1'

def get_as_unix_time(date_time):
    return calendar.timegm(date_time.utctimetuple())

def get_date_string_as_time(datestr):
    mydate = datetime.datetime.strptime(datestr, '%Y-%m-%d')
    return get_as_unix_time(mydate)

def get_now_str():
    return datetime.datetime.now().strftime('%Y-%m-%d')

class MyTypicalDynamoDbTableForProtobufs(object):
    def __init__(self, tablestr):
        self.tablestr = tablestr
        self.conn = self.get_conn()
        
    def get_conn(self):
        #get secret stuff
        access_key_id = os.getenv(k_env_name_for_amazon_id)
        secret_access_key = os.getenv(k_env_name_for_amazon_secret_key)

        conn = boto.dynamodb2.connect_to_region(k_region,
                aws_access_key_id=access_key_id,
                aws_secret_access_key=secret_access_key)
                
        return conn
        
    def get_table(self):
        table = Table(self.tablestr, connection=self.conn) #takes string argument
        print 'got table for ', self.tablestr
        return table
        
    def get_latest_item(self, account_id,datestr):
        table = self.get_table()
        res = table.query_2(account_id__eq=account_id,date__lte=datestr,limit=1,reverse=True)

        res2 = []
        for r in res:
            res2.append(r)
            
            
        params = None
        
        if len(res2) == 0:
            print 'no results found'
        else:
            print 'query date: ',datestr
            print 'model date: ',res2[0]['date']
            params = str(res2[0]['model_params'])

        
        return params

        
    def close(self):
        self.conn.close()

class UserModel(object):
    def __init__(self,protobuf):
        self.pb = online_hmm_pb2.AlphabetHmmUserModel()
        self.pb.ParseFromString(protobuf)
        
    def print_model(self):
        mydict = {}
        probs = []
        for vi in self.pb.vote_info:
            key = vi.output_id + ':' + vi.model_id
            mydict[key] = vi.probability_of_model
            probs.append(vi.probability_of_model)

        print np.sum(np.array(probs))        
        hist(probs,30); title('%d keys' % (len(probs))); show()
        

        
if __name__ == '__main__':
    #db = SleepHmmDynamoDB('sleephmm')
    #db.update_latest_item(-2, 'AABBDD')
    #db.close()
    
    parser = argparse.ArgumentParser()
    parser.add_argument("-f",  "--file", help="protobuf file in base64", required=False, default=None, type=str)
    parser.add_argument("--db", help="which database table in dynamo", default='online_hmm_models', type=str)
    parser.add_argument("-u",  "--user",  help='which user id to write to', required=True, type=str)
    parser.add_argument("--date",default=get_now_str(),help='date of at which this thing was created',required=False,type=str)
    args = parser.parse_args()
    
    #unixtime = get_date_string_as_time(args.date)

    protofile = args.file
    user = args.user
    
    db = MyTypicalDynamoDbTableForProtobufs(args.db)
    
    protobuf = db.get_latest_item(user,args.date)

    um = UserModel(protobuf)
    um.print_model()
    
    db.close()
