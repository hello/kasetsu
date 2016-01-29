#!/usr/bin/python
import random
import csv
import copy
import sys
import os


def randomize_and_split(mylist):
    randlist = copy.deepcopy(mylist)
    random.shuffle(randlist)
    N = len(randlist) / 2
    list1 = [randlist[i] for i in range(0,N)]
    list2 = [randlist[i] for i in range(N,len(randlist))]

    return list1,list2



def read_csv(csvfilename):
    rows = []
    with open(csvfilename, 'rb') as csvfile:
        reader = csv.reader(csvfile, delimiter=',')
        for row in reader:
            for i in range(len(row)):
                row[i] = row[i].strip()
            rows.append(row)

    print 'found %d rows' % len(rows)
    return rows


def write_csv(csvfilename,items):
    count = 0
    with open(csvfilename,'w') as csvfile:
        for item in items:
            csvfile.write(item[0] + ',')
            count += 1

    print 'wrote %d rows to %s' % (count,csvfilename)

def write_sql(filename,items,group_id,fileargs):
    with open(filename,fileargs) as sqlfile:
        sqlstring = 'INSERT INTO user_timeline_test_group (account_id,utc_ts,group_id) VALUES({},NOW(),{}); '
        for item in items:
            sqlfile.write(sqlstring.format(item[0],group_id) + '\n')

            
 


def main():
    random.seed(0)

    rows = read_csv(sys.argv[1])
    testname = sys.argv[2]
    group_id_a = sys.argv[3]
    group_id_b = sys.argv[4]
    
    agroup,bgroup = randomize_and_split(rows)

    filename = testname + '.sql'
    write_csv('agroup.csv',agroup)
    write_csv('brgroup.csv',bgroup)
    write_sql(filename,agroup,group_id_a,'w')
    write_sql(filename,bgroup,group_id_b,'a')

if __name__=='__main__':
    main()

