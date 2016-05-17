#!/bin/bash
echo "A Group"
psql -h common-replica-1.cdawj8qazvva.us-east-1.rds.amazonaws.com -d common -U common -f get_A_group_complaint_count.sql
echo "B Group"
psql -h common-replica-1.cdawj8qazvva.us-east-1.rds.amazonaws.com -d common -U common -f get_B_group_complaint_count.sql

