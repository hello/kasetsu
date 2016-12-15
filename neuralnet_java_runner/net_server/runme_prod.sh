#!/bin/bash
./app.py -c ./config.prod.ini -p 5551 &
./app.py -c ./config.prod.ini -p 5552 &
./app.py -c ./config.prod.ini -p 5553 &
./app.py -c ./config.prod.ini -p 5554 &
