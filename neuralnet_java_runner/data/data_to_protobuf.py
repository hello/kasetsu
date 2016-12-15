
import timeline_sensor_data_pb2
from collections import defaultdict
import csv
import datetime
import pytz
import calendar
import base64

pill_data_file = 'all_pill.csv000'
partner_pill_data_file = 'all_partner_pill.csv000'
sense_data_file = 'all_sense_data.csv000'

def read_pill_file(filename):
    pill_data = defaultdict(list)

    with open(filename, 'rb') as csvfile:
        reader = csv.reader(csvfile, delimiter=',')
        #aggregate by acccount id and evening
        for line in reader:
            key = line[0] + '_' + line[1]
            pill_data[key].append(line[2::])

    return pill_data

def read_partner_pill_file(filename):
    pill_data = defaultdict(list)

    with open(filename, 'rb') as csvfile:
        reader = csv.reader(csvfile, delimiter=',')
        #aggregate by acccount id and evening
        for line in reader:
            key = line[0] + '_' + line[2]
            pill_data[key].append(line[3::])

    return pill_data

def read_sense_file(filename):
    sense_data = defaultdict(list)

    with open(filename, 'rb') as csvfile:
        reader = csv.reader(csvfile, delimiter=',')
        for line in reader:
            key = line[1] + '_' + line[0]
            sense_data[key].append(line[2::])
            
    return sense_data

def string_to_utc_timestamp(timestr):
    dt = datetime.datetime.strptime(timestr, '%Y-%m-%d %H:%M:%S').replace(tzinfo=pytz.utc)
    return calendar.timegm(dt.utctimetuple())

def pill_line_to_tracker_motion(pill_line,m):
    m.timestamp = string_to_utc_timestamp(pill_line[0]) * 1000
    m.tz_offset = int(pill_line[1])
    m.svm_mag = int(pill_line[2])
    m.on_duration = int(pill_line[3])
    return m

def sense_line_to_sense_data(sense_line,protobuf):
    timestamp = string_to_utc_timestamp(sense_line[0]) * 1000
    offset = int(sense_line[1])

    vals = [protobuf.light_lux.add(),protobuf.waves.add(),protobuf.audio_peak_disturbance_db.add(),protobuf.audio_num_disturbances_db.add()]

    for i in range(4):
        vals[i].timestamp = timestamp
        vals[i].tz_offset = offset
        vals[i].value = float(sense_line[2+i])
            
    
def data_to_protobuf(pill_data,partner_pill_data,sense_data,outfile):
    keys = pill_data.keys()

    for key in keys:
        if not sense_data.has_key(key):
            print "%s has no sense data" % key
            continue
        
        pill_by_userday = pill_data[key]
        sense_by_userday = sense_data[key]
        partner_pill_by_userday = partner_pill_data[key]

        keyinfo = key.split('_')
        account_id = int(keyinfo[0])
        evening = keyinfo[1].split(' ')[0]
        
        protobuf = timeline_sensor_data_pb2.OneDaysSensorData()
        
        for line in pill_by_userday:
            pill_line_to_tracker_motion(line,protobuf.my_motion.add())

        for line in pill_by_userday:
            pill_line_to_tracker_motion(line,protobuf.partner_motion.add())

        for line in sense_by_userday:
            sense_line_to_sense_data(line,protobuf)

        protobuf.account_id = account_id
        protobuf.date_of_night = evening

        //TODO include account info
        outfile.write(base64.b64encode(protobuf.SerializeToString()) + '\n')

        

                


pill_data = read_pill_file(pill_data_file)
partner_pill_data = read_partner_pill_file(partner_pill_data_file)
sense_data = read_sense_file(sense_data_file)

data_to_protobuf(pill_data,partner_pill_data,sense_data)

print pill_data[pill_data.keys()[0]]
