#!/usr/bin/python
import psycopg2
import os
import datetime
import time

k_secret_key = 'qcg7PZiTOvzIBLpVKT/KhBNhIOfZVLJnjYblCCTE'
k_access_key_id = 'AKIAJBXIFRCYN4NNQENQ'
k_start_date = datetime.datetime(2016,1,1)
k_num_days = 90

def main():
    conn = psycopg2.connect("dbname='sensors1' user='benjo' host='sensors2.cy7n0vzxfedi.us-east-1.redshift.amazonaws.com' port=5439 password='N33dzmoarcoffee'")
    #f = open('query.str','r')
    f = open('query_any_event.str','r')
    query_str = f.read()
    f.close()


    for i in range(k_num_days):
        queryday = k_start_date + datetime.timedelta(i)
        query = get_query(query_str,queryday)
         

        cur = conn.cursor()
        #cur.execute("SELECT * FROM timeline_feedback WHERE account_id=1012 AND date_of_night > '2016-01-01'")
        tic1 = time.time()
        cur.execute(query)
        tic2 = time.time()

        print tic2 - tic1

def get_query(querystr,date):
    todaystr = date.strftime('%Y-%m-%d')
    tomorrowstr = (date + datetime.timedelta(1)).strftime('%Y-%m-%d')
    return  querystr.format(todaystr,tomorrowstr,k_access_key_id,k_secret_key)
    

if __name__=='__main__':
    main()


