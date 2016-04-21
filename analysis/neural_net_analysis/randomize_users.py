#!/usr/bin/python

import sys
import csv
import datetime
import calendar
import numpy as np
import random
import copy



             
            
def randomize_and_split(mylist):
    randlist = copy.deepcopy(mylist)
    random.shuffle(randlist)
    N = len(randlist) / 2
    list1 = [randlist[i] for i in range(0,N)]
    list2 = [randlist[i] for i in range(N,len(randlist))]

    return list1,list2

def read_accounts(filename):
    accounts = []
    with open(filename,'r') as f:
        reader = csv.reader(f,delimiter=',')
        for line in reader:
            accounts.append(line[0])


    return accounts

def write_accounts_list(mylist,filename):
    print 'writing %s with %d items' % (filename,len(mylist))

    with open(filename,'w') as f:
        for item in mylist:
            if item != mylist[0]:
                f.write(',')
                
            f.write(item)

 
                


def main():
    accounts = read_accounts(sys.argv[1])
    accsA,accsB = randomize_and_split(accounts)
    write_accounts_list(accsA,'A_group.csv') 
    write_accounts_list(accsB,'B_group.csv') 
 

            

if __name__ == '__main__':
    if len(sys.argv) <= 1:
        print 'requires input file'
        sys.exit(0)

    main()


                                

                                
