#!/usr/bin/python
import sys
import csv
import numpy as np
headers = ['account_id','query_date','event_type','prediction_error','orig_error']

k_input_file = 'part_pred_err.csv'
k_err_threshold = 20
k_improvement_margin = 10

def print_report(event_type,results):
    fuck_up_count,fail_count,improved_count,success_count,no_change_count,switched_count,total_count = results
    
    percents = np.array([fail_count,no_change_count,improved_count,success_count,switched_count,fuck_up_count]) / float(total_count)

    names = ['all predictions that were failures',
             'all predictions not successful or failed which did not make things better',
             'all predictions not successful or failed which improved the prediction',
             'all predictions that were successful',
             'predictions switched from failure to success (GOOD)',
             'predictions switched from success to failure (BAD)']

    print '\n\n\n'
    print 'PARTNER FILTER PREDICTIONS: ',event_type
    print '-------------------------------------------------------'
    for i in range(len(names)):
        print '%3.1f%%' % (int(percents[i] * 1000) / 10.0), '\t' ,names[i]
        
    print total_count,'\t','total number of predictions'


def process_errors(events,is_positive_err_failure,err_threshold):
    fail_count = 0
    success_count = 0
    no_change_count = 0
    fuck_up_count = 0
    improved_count = 0
    switched_count = 0
    total_count = 0
    
    for row in events:

    
        
        is_screwed_up_something_that_was_already_good = False
        is_fail = False
        is_success = False
        is_improved = False
        is_switched = False
        
        if is_positive_err_failure:
            if row[0] > k_err_threshold:
                is_fail = True                   
        else:
            if row[0] < -k_err_threshold:
                is_fail = True

        #did we screw up something that was already good?
        if is_fail and abs(row[1]) < k_err_threshold:
                is_screwed_up_something_that_was_already_good = True

        if not is_fail:
            #if prediction error is less than threshold and the original prediction was not good
            if abs(row[0]) < err_threshold:  
                is_success = True
                if abs(row[1]) >= err_threshold:
                    is_switched = True

            #if things are just generally improved
            if abs(row[0]) < (abs(row[1]) - k_improvement_margin) and not is_success:
                is_improved = True


        if is_fail:
            fail_count += 1

        if is_success:
            success_count += 1
            
        if not is_fail and not is_success and not is_improved:
            no_change_count += 1

        if is_screwed_up_something_that_was_already_good:
            fuck_up_count += 1

        if is_improved:
            improved_count += 1

        if is_switched:
            switched_count += 1

        total_count += 1


    return fuck_up_count,fail_count,improved_count,success_count,no_change_count,switched_count,total_count

        

if __name__ == '__main__':
    f = open(k_input_file,'r')

    reader = csv.DictReader(f)

    mydict = {'IN_BED' : [],'OUT_OF_BED' : []}
    
    for row in reader:
        event_type = row['event_type']
        pred_error = int(row['prediction_error'])
        orig_error = int(row['orig_error'])

        mydict[event_type].append([pred_error,orig_error])

    f.close()

    results1 = process_errors(mydict['IN_BED'],False,k_err_threshold)
    results2 = process_errors(mydict['OUT_OF_BED'],True,k_err_threshold)

    print_report('IN_BED',results1)
    print_report('OUT_OF_BED',results2)
    


    
    
        
