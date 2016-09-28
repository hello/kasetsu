#!/bin/bash
#play -t ima -r 16000 $1
./adpcm -d -o /tmp/$1 -i $1 > /dev/null
./convert_raw_to_wav.sh /tmp/$1 /tmp/$1.wav > /dev/null
mplayer /tmp/$1.wav
