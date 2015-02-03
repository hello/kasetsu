#!/usr/bin/python
import requests
import sys
from pylab import *
from numpy import *
import dbdata

from copy import *
import datetime

#v1/datascience/admin/pill/{email}/{query_date_local_utc}
pill_url = 'https://dev-api.hello.is/v1/datascience/admin/pill/'
label_url = 'https://dev-api.hello.is/v1/datascience/label/'
auth = '10.d812154f46e641eeb70386155b977cb6'
k_num_days = 20
k_emails = ['kingshy+d3@sayhello.com','p31@sayhello.com','rshok2+1@gmail.com','jimmy5570@sayhello.com','benjo4@sayhello.com','delisa+dvt@sayhello.com']

def get_unix_time_as_datetime(unix_time):
    return datetime.datetime.utcfromtimestamp(unix_time)
    
def pull_data_from_server(date, email):
    target_date_string = date.isoformat()
    
    headers = {'Authorization' : 'Bearer %s' % auth}
    url = pill_url + email + '/'+ target_date_string
    response = requests.get(url,params={},headers = headers)
    
    if  response.ok:
        
        pill_data = response.json()
        
        url = label_url + email + '/'+ target_date_string
        response = requests.get(url,params={},headers = headers)
        
        if  response.ok:
            
            label_data = response.json()
        
            return pill_data, label_data
    
    else:
        return (None, None)
        
        
        
def plot_data(email, pd, ld, pred_times):
    #{u'account_id': 1744, u'motion_range': 0, u'timestamp': 1422721980000, u'timezone_offset': -28800000, u'kickoff_counts': 1, u'value': 177, u'tracker_id': 1156, u'on_duration_seconds': 1, u'id': 666426
    #{u'duration_millis': 0, u'tz_offset': -28800000, u'label': u'went_to_bed', u'note': u'- created by benjo@sayhello.com at <function get_current_pacific_datetime at 0xfb9614b0>', u'ts_utc': 1422689460000, u'night': u'2015-01-30', u'email': u'benjo4@sayhello.com'}, 
    tpd = [get_unix_time_as_datetime(int(f['timestamp']/1000.0)) for f in pd]
    apd = array([f['value'] for f in pd])
    
    tld = [get_unix_time_as_datetime(int(f['ts_utc']/1000.0)) for f in ld]
   
    label = [f['label'] for f in ld]
    plot(tpd, apd, '.-')
    
    for i in xrange(len(tld)):
        text(tld[i], 0, label[i], rotation=45)
    
    plot(tld, zeros((len(tld))), 'rd')

    if pred_times is not None:
        pt = array(pred_times)
        
        for k in xrange(pt.shape[0]):
            row = pt[k, :]
            yval = 100
            plot(row[0], yval, 'k>')
            plot(row[3], yval, 'k<')
            plot([row[1], row[2]], [yval, yval], 'k.-')
        
    grid('on')
    title(email)
    show()

if __name__ == '__main__':

    predictdict = {}

    if len(sys.argv) >= 2:
        import csv
        d = dbdata.DataGetter('benjo','benjo','localhost')
        mymap = d.get_user_email_map() #returns user ID from email
        
        with open(sys.argv[1]) as csvfile:
            myreader = csv.reader(csvfile, delimiter=',')
       
            for row in myreader:
                val = int(row[0])
                if mymap.has_key(val):
                    key = mymap[val]
                    
                    if key not in predictdict:
                        predictdict[key] = []
                    
                    predictdict[key].append([get_unix_time_as_datetime(float(row[1])), get_unix_time_as_datetime(float(row[2])), get_unix_time_as_datetime(float(row[3])), get_unix_time_as_datetime(float(row[4]))])
                else:
                    print 'skipping ',  row[0]
                
        
    for email in k_emails:
        d = datetime.date(2015, 1, 20)

        pd = []
        ld = []
        dt = datetime.timedelta(days=1)
        for i in xrange(k_num_days):
            pill_data, label_data = pull_data_from_server(d, email)
            
            d += dt

            if pill_data is None:
                continue
                
            pd.extend(pill_data)
            ld.extend(label_data)
            

        pred_times = []
        if predictdict.has_key(email):
            pred_times = predictdict[email]
            
        print len(pd), len(ld), len(pred_times)
        
        plot_data(email, pd, ld, pred_times)
            
