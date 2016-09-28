#!/bin/bash
LIMIT=3
for account in $(cat accounts.txt)
do
   #echo $account
  command="python debug.py --key=AKIAJ5F7MY4477II5GTA --secret=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 --account=$account --limit=$LIMIT --download=True"
  eval $command
done

