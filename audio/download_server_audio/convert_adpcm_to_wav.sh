#!/bin/bash
./adpcm -d -o /tmp/$1 -i $1 > /dev/null
./convert_raw_to_wav.sh /tmp/$1 $1.wav > /dev/null
