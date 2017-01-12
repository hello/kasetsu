import boto
from boto.s3.connection import S3Connection
from boto.s3.key import Key
import os
import sys
import gzip
import json
import datetime
import json
import subprocess

k_filters = ['+okay_sense']

def read_json_parts(file_contents):
    datas = file_contents.split("}")

    lines = []

    for data in datas:
        if len(data) <= 2:
            continue

        line_data = data + "}"
        jdata = json.loads(line_data)

        this_id = jdata['id']

        is_good = False
        for filtertxt in k_filters:
            if this_id.find(filtertxt) != -1:
                is_good = True

        if not is_good:
            continue

        lines.append(line_data)
        #n = jdata['num_cols']
        #bindata = base64.b64decode(jdata['payload'])
        timestr = (datetime.datetime.fromtimestamp(jdata['timestamp_utc']/1000)).strftime('%Y-%m-%d %H:%M:%S')

    return lines
        
def get_files():
    all_lines = []
    for root, dirs, files in os.walk(sys.argv[1]):
        for f in files:
            fileparts = f.split('.')
            if fileparts[-1] != 'gz':
                continue
            
            gz = gzip.GzipFile(os.path.join(root, f),'r')

            all_lines.extend(read_json_parts(gz.read()))
            
    with open(sys.argv[2],'w') as outfile:
        for line in all_lines:
            outfile.write(line + '\n')

if __name__ == '__main__':
    get_files()
