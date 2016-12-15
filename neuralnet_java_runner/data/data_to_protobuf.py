
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
demography_data_file = 'demography.csv'

def read_pill_file(filename):
    pill_data = defaultdict(list)

    with open(filename, 'rb') as csvfile:
        reader = csv.reader(csvfile, delimiter=',')
        #aggregate by acccount id and evening
        for line in reader:
            if len(line) == 0:
                continue
            
            key = line[0] + '_' + line[1]
            pill_data[key].append(line[2::])

    return pill_data

def read_partner_pill_file(filename):
    pill_data = defaultdict(list)

    with open(filename, 'rb') as csvfile:
        reader = csv.reader(csvfile, delimiter=',')
        #aggregate by acccount id and evening
        for line in reader:
            if len(line) == 0:
                continue
            
            key = line[0] + '_' + line[2]
            pill_data[key].append(line[3::])

    return pill_data

def read_sense_file(filename):
    sense_data = defaultdict(list)

    with open(filename, 'rb') as csvfile:
        reader = csv.reader(csvfile, delimiter=',')
        for line in reader:

            if len(line) == 0:
                continue
            
            key = line[1] + '_' + line[0]
            sense_data[key].append(line[2::])
            
    return sense_data

def read_demography_file(filename):
    demodata = defaultdict(list)

    with open(filename, 'rb') as csvfile:
        reader = csv.reader(csvfile, delimiter=',')
        for line in reader:

            if len(line) == 0:
                continue
            
            key = int(line[1]) #just account_id here
            demodata[key].append(line[2::])
            
    return demodata

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
            
def demodata_to_protobuf(account_id,demo_data,protobuf):

    demo_data_by_account = demo_data[account_id]

    if len(demo_data_by_account) == 0:
        print 'no demographics found for user %d' % account_id
        return

    line = demo_data_by_account[0]
    
    protobuf.user_info.weight_grams = int(float(line[1]))
    protobuf.user_info.height_cm = int(float(line[0]))
    protobuf.user_info.date_of_birth= line[3]

    genderstr = line[4]
    protobuf.user_info.gender = timeline_sensor_data_pb2.Gender.Value(genderstr)


def data_to_protobuf(pill_data,partner_pill_data,sense_data,demo_data,outfile):
    keys = pill_data.keys()
    print len(keys)
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

        demodata_to_protobuf(account_id,demo_data,protobuf)
        
        for line in pill_by_userday:
            pill_line_to_tracker_motion(line,protobuf.my_motion.add())

        for line in pill_by_userday:
            pill_line_to_tracker_motion(line,protobuf.partner_motion.add())

        for line in sense_by_userday:
            sense_line_to_sense_data(line,protobuf)

        protobuf.account_id = account_id
        protobuf.date_of_night = evening

        #TODO include account info
        outfile.write(base64.b64encode(protobuf.SerializeToString()) + '\n')

        

def main():
    print 'reading demographic data from %s' % demography_data_file
    demo_data = read_demography_file(demography_data_file)

    print 'reading pill data from %s' % pill_data_file
    pill_data = read_pill_file(pill_data_file)

    print 'reading partner pill data from %s' % partner_pill_data_file
    partner_pill_data = read_partner_pill_file(partner_pill_data_file)

    print 'reading sense data from %s' % sense_data_file
    sense_data = read_sense_file(sense_data_file)

    
    f = open('outfile.dat','wb')
    data_to_protobuf(pill_data,partner_pill_data,sense_data,demo_data,f)
    f.close()

if __name__ == '__main__':
    main()
