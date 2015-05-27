#!/bin/bash

./parallel_pull_timeline.py -i Test\ dataset\ -\ Ground\ Truths.csv -o bars.csv --p 16
./process_results.py -i bars.csv
