#!/bin/bash

tmpfile=$(mktemp /tmp/adpcmconvert.XXXXXX)
./adpcm -d -o $tmpfile -i $1 > /dev/null
./convert_raw_to_wav.sh $tmpfile $1.wav > /dev/null
rm $tmpfile
