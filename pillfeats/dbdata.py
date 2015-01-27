#!/usr/bin/python

import psycopg2
import time
import datetime

k_pill_table = 'tracker_motion_master'
k_sensor_table = 'device_sensors_master'

def get_as_unix_time(date_time):
    return time.mktime(date_time.timetuple())

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
        conn.close()
        
    
    def get_users(self):
        self.reinitialize()
        
        cur = self.conn.cursor()
            
        cur.execute("""SELECT account_id FROM %s GROUP BY account_id""" % (k_pill_table))
        
        users = cur.fetchall()
        
        return users
        
    def get_all_pill_data_after_date(self, datestr):
        
        self.reinitialize()
        
        cur = self.conn.cursor()
            
        cur.execute("""SELECT account_id,ts,svm_no_gravity FROM %s WHERE ts > \'%s\' AND svm_no_gravity > 0 """ % (k_pill_table, datestr))
        
        
        return cur.fetchall() 
        
        
    def get_all_sensor_data_after_date(self, datestr):
        self.reinitialize()
        
        cur = self.conn.cursor()
            
        cur.execute("""SELECT account_id,ts,ambient_light FROM %s WHERE ts > \'%s\' ORDER BY account_id,ts""" % (k_sensor_table, datestr))
        
        
        return cur.fetchall() 
        
        
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
        
    def do_all(self, min_num_pill_data):
        print ('getting significant light data')
        self.light = self.get_significant_light_events('2015-01-01')
        
        print ('getting pill data')
        self.pill = self.get_all_pill_data_after_date('2015-01-01')
        
        self.data = self.join_pill_and_light(self.pill, self.light)
        
        badkeys = []
        for key in self.data:
            if len(self.data[key]['pill'][0]) < min_num_pill_data:
                badkeys.append(self.data[key])
                
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
                
                
