#!/usr/bin/python
import serverdata
import argparse
import csv
import numpy

k_user_list = [1 ,  1001 ,  1002 ,  1005 ,  1012 ,  1013 ,  1025  , 1038 ,  1043    , 1052 ,  1053 ,  1060  , 1061 ,  1062 ,  1063 ,  1067 ,  1070 ,  1071 ,  1072 ,1310  , 1609 ,  1629 ,  1648]
#k_user_list = [1012]

def pull_data(params, date, num_days): 
 
    print 'querying DB'  
    user_list = k_user_list
    
    min_date = date
        
    a = serverdata.BinnedDataGetter(user_list,params)
    data = a.get_all_binned_data(min_date,num_days)
    
    #flatten
    flatdata = []
    for key in data:
        flatdata.extend(data[key]['data'])
    
    flatdata = numpy.array(flatdata).transpose().tolist()
    
    return flatdata

if __name__ == '__main__':
    params = {
    'pill_magnitude_disturbance_threshold_lsb' : 12000, 
    'audio_disturbance_threshold_db' : 65, 
    'natural_light_filter_start_hour' : 16.0, 
    'natural_light_filter_stop_hour' : 4.0,
    'meas_period_minutes' : 15}

    parser = argparse.ArgumentParser()
    parser.add_argument('--date', help = 'target date', required=True)
    parser.add_argument('-n','--numdays',default=1, help = 'num days to retrieve')
    parser.add_argument('-o','--outfile', required=True)
    args = parser.parse_args()

    data = pull_data(params,args.date, args.numdays)
        
    with open(args.outfile, 'wb') as csvfile:
        writer = csv.writer(csvfile, delimiter=',')
        for row in data:
            writer.writerow(row)
    
