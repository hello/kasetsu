#!/usr/bin/python

import psycopg2
import time
import datetime
import json

k_pill_table = 'tracker_motion_master'
k_sensor_table = 'device_sensors_master'

def get_as_unix_time(date_time):
    return time.mktime(date_time.timetuple())

def get_common(a, b, keya, keyb):
    newdict = {}
    
    sa = set(a.keys())
    sb = set(b.keys())
    
    goodkeys = sa.intersection(sb)
    
    for key in goodkeys:
        newdict[key] = {}
        newdict[key][keya] = a[key]
        newdict[key][keyb]=  b[key]
        
    return newdict

class DataGetter(object):
    def __init__(self, dbname, user, host, pw = None):
        self.conn = None
        self.dbname = dbname
        self.user = user
        self.host = host
        self.pw = pw
        
    def reinitialize(self):
        ready = False
        if self.conn is not None:
            ready = not self.conn.closed
        
        if not ready:
            self.conn = psycopg2.connect(dbname=self.dbname,user=self.user,host=self.host)
        
    def deinitialize(self):
        self.conn.close()
        
    
    def get_users(self):
        self.reinitialize()
        
        cur = self.conn.cursor()
            
        cur.execute("""SELECT account_id FROM %s GROUP BY account_id""" % (k_pill_table))
        
        users = cur.fetchall()
        
        return users
        
    def get_all_minute_data(self, datestr, min_num_records, min_num_pill_records):
        self.reinitialize()
        
        cur = self.conn.cursor()
        
        query = """
         
        SELECT 
            device_sensors_master.account_id,
            device_sensors_master.ts,
            device_sensors_master.ambient_light,
            device_sensors_master.audio_num_disturbances,
            tracker_motion_master.svm_no_gravity
        FROM
            device_sensors_master
            
            LEFT OUTER JOIN tracker_motion_master ON 
                device_sensors_master.account_id = tracker_motion_master.account_id
                AND 
                device_sensors_master.ts = tracker_motion_master.ts
                
        WHERE
            device_sensors_master.ts > \'%s\'
        ORDER BY
            device_sensors_master.account_id,device_sensors_master.ts
            
        """ % (datestr)
        
        #print query
        
        cur.execute(query)
        records = cur.fetchall()
        
        datadict = {}
        for record in records:
            key = record[0]
            if not datadict.has_key(record[0]):
                datadict[key] = [[], [], [], []]
                
            datadict[key][0].append(get_as_unix_time(record[1]))
            datadict[key][1].append(record[2])
            datadict[key][2].append(record[3])
            datadict[key][3].append(record[4])

            
        badkeys = []
        for key in datadict:
            if len(datadict[key][0]) < min_num_records:
                badkeys.append(key)
                continue
                
            pill_data = datadict[key][3]
            pill_counts = 0
            for p in pill_data:
                if p != None:
                    pill_counts += 1;
                    
            if pill_counts < min_num_pill_records:
                badkeys.append(key)
                
        for key in badkeys:
            del datadict[key]

        return datadict

        
        
    def get_all_pill_data_after_date(self, datestr, min_num_records = 0):
        
        self.reinitialize()
        
        cur = self.conn.cursor()
            
        cur.execute("""SELECT account_id,ts,svm_no_gravity FROM %s WHERE ts > \'%s\' AND svm_no_gravity > 0 """ % (k_pill_table, datestr))
        
        records = cur.fetchall() 
        
        datadict = {}
        for record in records:
            key = record[0]
            if not datadict.has_key(record[0]):
                datadict[key] = [[], []]
                
            datadict[key][0].append(record[1])
            datadict[key][1].append(record[2])
            
        badkeys = []
        for key in datadict:
            if len(datadict[key][0]) < min_num_records:
                badkeys.append(key)
                
        for key in badkeys:
            del datadict[key]

        return datadict
        
        
        
        
    def get_all_sensor_data_after_date(self, datestr, min_num_records = 0):
        self.reinitialize()
        
        cur = self.conn.cursor()
            
        query = """ 
          
                SELECT
                    account_id,ts,ambient_light
                FROM
                    %s
                WHERE 
                    ts >  \'%s\'
                ORDER BY
                    account_id,ts
            
            
        
                """ % (k_sensor_table, datestr)
        
        cur.execute(query)
        
        
        records = cur.fetchall() 
        
        datadict = {}
        for record in records:
            key = record[0]
            if not datadict.has_key(record[0]):
                datadict[key] = [[], []]
                
            datadict[key][0].append(record[1])
            datadict[key][1].append(record[2])
            
        badkeys = []
        for key in datadict:
            if len(datadict[key][0]) < min_num_records:
                badkeys.append(key)
                
        for key in badkeys:
            del datadict[key]

        return datadict
        
    def get_all_sensor_data_after_date_by_account_id(self, datestr, accountid):
        self.reinitialize()
        
        cur = self.conn.cursor()
            
        cur.execute("""SELECT account_id,ts,ambient_light FROM %s WHERE ts > \'%s\' AND account_id=%d ORDER BY account_id,ts""" 
        % (k_sensor_table, datestr, int(accountid)))
        
        
        return cur.fetchall() 
        
    def get_significant_light_events(self, datestr):
        self.reinitialize()
        
        cur = self.conn.cursor()
            
        cur.execute("""
        
   
        SELECT
            light1.account_id,
            light1.ts,
            light1.ambient_light,
            light1.prev_light
        FROM
            (SELECT 
                account_id,
                ts,
                ambient_light,
                lag(ambient_light) OVER (PARTITION BY account_id ORDER BY ts) as prev_light
            FROM 
                %s 
            
            WHERE 
                ts > \'%s\' AND
                ambient_light >= 0
            ORDER BY 
                account_id,ts) as light1
        WHERE
            abs(ln(light1.ambient_light + 1.0) - ln(light1.prev_light + 1.0)) > 1.0 
        ORDER BY
            light1.account_id,
            light1.ts
        ;
        """ % (k_sensor_table, datestr))
        
        
        return cur.fetchall() 
        
    def do_all(self, min_num_pill_data, datestr):
        print ('getting significant light data')
        self.light = self.get_significant_light_events(datestr)
        
        print ('getting pill data')
        self.pill = self.get_all_pill_data_after_date(datestr)
        
        self.data = self.join_pill_and_light(self.pill, self.light)
        
        badkeys = []
        for key in self.data:
            if len(self.data[key]['pill'][0]) < min_num_pill_data:
                badkeys.append(key)
                
        for key in badkeys:
            del(self.data[key])
                
                
        
        
    def join_pill_and_light(self, pill, light):
        
        mydict = {}
        for item in pill:
            key = item[0]
            
            if not mydict.has_key(key):
                mydict[key] = {'pill' : [[], []],  'sense' : [ [], [], []]}
               
                
            my_list = mydict[key]['pill']
            my_list[0].append(get_as_unix_time(item[1]))
            my_list[1].append(item[2])
            
        
        for item in light:
            key = item[0]
            
            if not mydict.has_key(key):
                mydict[key] = {'pill' : [[], []],  'sense' : [ [], [], []]}
                
            my_list = mydict[key]['sense']
            my_list[0].append(get_as_unix_time(item[1]))
            my_list[1].append(item[2])
            my_list[2].append(item[3])

        return mydict
                
    def save(self, filename):
        f = open(filename, 'w')
        json.dump(self.data, f)
        f.close()
        
    def load(self, filename):
        f = open(filename, 'r')
        self.data = json.load(f)
        f.close()
