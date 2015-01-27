#!/usr/bin/python

import psycopg2

k_pill_table = 'tracker_motion_master'
k_sensor_table = 'device_sensors_master'

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
            
        cur.execute("""SELECT account_id,ts,svm_no_gravity FROM %s WHERE ts > \'%s\' """ % (k_pill_table, datestr))
        
        
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
            abs(ln(light1.ambient_light + 1.0) - ln(light1.prev_light + 1.0)) > 2.0 
        ORDER BY
            light1.account_id,
            light1.ts
        ;
        """ % (k_sensor_table, datestr))
        
        
        return cur.fetchall() 
