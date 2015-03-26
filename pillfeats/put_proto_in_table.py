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
import calendar
import datetime
from time import strftime

k_env_name_for_amazon_id = 'AWS_ACCESS_KEY_ID'
k_env_name_for_amazon_secret_key = 'AWS_SECRET_KEY'
k_region = 'us-east-1'

def get_as_unix_time(date_time):
    return calendar.timegm(date_time.utctimetuple())

def get_date_string_as_time(datestr):
    mydate = datetime.datetime.strptime(datestr, '%Y-%m-%d')
    return get_as_unix_time(mydate)

class SleepHmmDynamoDB(object):
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
        
    def update_latest_item(self, id, blob,unixtime = None):
        table = self.get_table()
        res = table.scan(account_id__eq=id)
        
        max_date = 0
        for r in res:
            d = r['create_date']
            if max_date < d:
                max_date = d
        
        if unixtime != None:
            max_date = unixtime

        print 'max date was ', max_date
        table.put_item(data={'account_id' : id,  'create_date' : max_date,  'model' : Binary(blob)}, overwrite=True)
        
    def close(self):
        self.conn.close()
        
        
if __name__ == '__main__':
    #db = SleepHmmDynamoDB('sleephmm')
    #db.update_latest_item(-2, 'AABBDD')
    #db.close()
    
    parser = argparse.ArgumentParser()
    parser.add_argument("-f",  "--file", help="protobuf file in base64", required=False, default=None, type=str)
    parser.add_argument("--db", help="which database table in dynamo", default='sleephmm', type=str)
    parser.add_argument("-u",  "--user",  help='which user id to write to', required=True, type=int)
    parser.add_argument("--date",default='1970-01-01',help='date of at which this thing was created',required=False,type=str)
    args = parser.parse_args()
    
    unixtime = get_date_string_as_time(args.date)

    protofile = args.file
    user = args.user
    
    db = SleepHmmDynamoDB(args.db)
    
    f = open(protofile, 'r')
    protodata = f.read()
    f.close()
    
    bindata = base64.b64decode(protodata)
    
    db.update_latest_item(user, bindata,unixtime)
    
