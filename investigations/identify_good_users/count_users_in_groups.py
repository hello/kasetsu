#!/usr/bin/python

import sys
import csv
import csv

#  do this
# \copy (select * from timeline_analytics where date_of_night > '2015-11-16' and error=0) to /tmp/timeline_analytics.csv with CSV HEADER;
class Users(object):
    def __init__(self,filename):
        self.filename = filename

    def load(self):
        mydict = {}
        with open(self.filename) as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:

                account_id = row['account_id']

                if not mydict.has_key(account_id):
                    mydict[account_id] = 0

        self.users = []
        for key in mydict:
            self.users.append(key)
            
 
class Analytics(object):
    def __init__(self,filename,targetalg):
        self.filename = filename
        self.alg = targetalg


    def load(self):
        mydict = {}
        
        with open(self.filename) as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                account_id = row['account_id']
                alg = row['algorithm']
                error = row['error']
                
                if alg == 0:
                    continue #no alg

                if not mydict.has_key(account_id):
                    mydict[account_id] = (0,0)

                counts = mydict[account_id]

                if alg == self.alg:
                    counts = (counts[0] + 1,counts[1])
                else:
                    counts = (counts[0],counts[1] + 1)

                mydict[account_id] = counts

            self.counts = mydict


    def sum_counts(self,users):
        #for user in self.counts:
 #           print self.counts[user]
            
        count = 0
        for user in users:
            if not self.counts.has_key(user):
                continue

            count += self.counts[user][0]

        return count
            

        


def main():
    a = Analytics(sys.argv[1],sys.argv[2])
    b = Users(sys.argv[3])
    a.load()
    b.load()

    print a.sum_counts(b.users)
    

if __name__ == '__main__':
    main()
                    
                
                
