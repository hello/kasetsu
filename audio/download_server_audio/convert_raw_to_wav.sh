#!/bin/bash
ffmpeg -f s16le -ar 16000 -ac 1 -i $1 -ar 16000 -ac 1 $2
