#!/usr/bin/python
import requests
import sys
from pylab import *
from numpy import *

from copy import *
import datetime

#v1/datascience/admin/pill/{email}/{query_date_local_utc}
pill_url = 'https://dev-api.hello.is/v1/datascience/admin/pill/'
label_url = 'https://dev-api.hello.is/v1/datascience/label/'
auth = '10.d812154f46e641eeb70386155b977cb6'
k_num_days = 15
k_emails = ['benjo4@sayhello.com','delisa+dvt@sayhello.com']

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
        
        
        
def plot_data(email, pd, ld):
    #{u'account_id': 1744, u'motion_range': 0, u'timestamp': 1422721980000, u'timezone_offset': -28800000, u'kickoff_counts': 1, u'value': 177, u'tracker_id': 1156, u'on_duration_seconds': 1, u'id': 666426
    #{u'duration_millis': 0, u'tz_offset': -28800000, u'label': u'went_to_bed', u'note': u'- created by benjo@sayhello.com at <function get_current_pacific_datetime at 0xfb9614b0>', u'ts_utc': 1422689460000, u'night': u'2015-01-30', u'email': u'benjo4@sayhello.com'}, 
    tpd = [get_unix_time_as_datetime(int(f['timestamp']/1000.0)) for f in pd]
    apd = array([f['value'] for f in pd])
    
    tld = [get_unix_time_as_datetime(int(f['ts_utc']/1000.0)) for f in ld]
    #print int(ld[0]['ts_utc']/1000.0)
    #print tld[0].timetuple()
    label = [f['label'] for f in ld]
    plot(tpd, apd, '.-')
    
    for i in xrange(len(tld)):
        text(tld[i], 0, label[i], rotation=45)
        
    plot(tld, zeros((len(tld))), 'o')
    grid('on')
    title(email)
    show()

if __name__ == '__main__':
    
    for email in k_emails:
        d = datetime.date(2015, 1, 20)

        pd = []
        ld = []
        dt = datetime.timedelta(days=1)
        for i in xrange(k_num_days):
            pill_data, label_data = pull_data_from_server(d, email)
            pd.extend(pill_data)
            ld.extend(label_data)
            d += dt
            

        plot_data(email, pd, ld)
            
            
