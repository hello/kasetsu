#!/bin/bash
ffmpeg -i $1 -f s16le -acodec pcm_s16le -ac 1 -ar 32000 $2
