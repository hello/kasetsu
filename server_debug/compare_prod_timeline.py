"""Script to pull time series data from device_sensors"""
import sys
import csv
from datetime import datetime, timedelta
import time
from rauth import OAuth2Service
import json
import arrow
import matplotlib.pyplot as plt
from  pylab import rcParams
import matplotlib.dates as md

import numpy

NO_PARTNER = False

ACCURACY_TOLERANCE = 20 # +/- 15 mins
START_DAY = datetime(2015, 1, 2, 0, 0)
EVENT_TYPES = ['IN_BED', 'SLEEP', 'WAKE_UP', 'OUT_OF_BED']
HEADERS = {'Content-type': 'application/json', 'Accept': 'application/json'}

PROD_URL = "https://api.hello.is/"
ADMIN_TOKEN = '1.2a040346e1ae4b669e33baac6bfe4c01'
DEV_URL = "http://0.0.0.0:9999/"

RESEARCH_URL = "http://ec2-52-1-32-223.compute-1.amazonaws.com/"
#RESEARCH_URL = 'https://research-api-benjo.hello.is/'
RESEARCH_TOKEN = '7.80d86f3b0f2443418663c320eaa98567'

ALGOS = {'HMM': 'hmm', 'WPA': 'sleep_score', 'VOTING': 'voting'}
PROD_HMM_ACCOUNTS = [1001, 1012, 1377, 1]

DETECT_TYPES = ['detected', 'missing']

TIME_FMT = "%Y-%m-%d %H:%M:%S"

#RESULTS_FOLDER = "/Users/kingshy/Dropbox_hello/Dropbox (Hello)/Product/Software/Research/Timeline_Data"
RESULTS_FOLDER = "./"

def read_user_tokens(filename):
    fp = open(filename)
    reader = csv.reader(fp)
    users = {}
    for row in reader:
        email, token, account_id = row
        users[email] = {'email': email, 'token': token, 'account_id': account_id}

    return users

def read_truths(filename):
    fp = open(filename)
    reader = csv.DictReader(fp)
    header = reader.next()

    times = {}
    for row in reader:
        account_id = row['account_id']
        email = row['email']
        night = row['day_of_night']
        inbed = row['in_bed']
        sleep = row['sleep']
        awake = row['awake']
        outbed = row['out_of_bed']
        
        has_partner = False
        if row.has_key('has_partner'):
            has_partner = row['has_partner'] in ['True', 'true', '1']
        
        if NO_PARTNER == True and has_partner == True:
            #print 'filtering ', row['email']
            continue
        
        labels = [inbed, sleep, awake, outbed]
    
        time_data = []
    
        if len(night) == 0:
            continue
    
        times.setdefault(email, {})
        for i in range(4):
            if len(labels[i]) == 0:
                time_data.append(None)
                continue
                
            date_string = "%s %s"% (night, labels[i])
            night_date = datetime.strptime(date_string, "%Y-%m-%d %H:%M")
            hour = night_date.hour
            if night_date.hour < 15:
                night_date = night_date + timedelta(days=1)
            time_data.append(night_date)                
        
        times[email][night] = {'email': email,
                            'account_id': account_id,
                            'IN_BED': time_data[0],
                            'SLEEP': time_data[1],
                            'WAKE_UP': time_data[2],
                            'OUT_OF_BED': time_data[3]
                            }
    return times

def get_session(token, url):
    hello = OAuth2Service(
            client_id='testing',
            client_secret="",
            name="hello",
            authorize_url=url + "oauth2/authorize",
            access_token_url=url + "oauth2/token",
            base_url=url)
    return hello.get_session(token)

def get_prediction(account_id, date_string):
    results = {}
    session = get_session(RESEARCH_TOKEN, RESEARCH_URL)
    if not session:
        return {}

    for algo in ALGOS:
        algorithm = ALGOS[algo]
        results[algo] = {}
        endpoint = "v1/prediction/sleep_events/%s/%s?algorithm=%s" % (
                        account_id, date_string, algorithm)
        api_url = "%s%s" % (RESEARCH_URL, endpoint)
        response = session.get(api_url, headers=HEADERS)
        data = json.loads(response.content)

        if data == 404:
            print api_url
            continue

        if len(data) == 0:
            continue

       
        for event in data:
            offset = timedelta(seconds=event['timezoneOffset']/1000)
            event_time = datetime.utcfromtimestamp(event['startTimestamp']/1000) + offset
            etype = event['type']
            #if first sleep or in_bed is already there, then skip
            if algo == 'HMM' and etype in ['SLEEP', 'IN_BED']:
                if etype in results[algo]:
                    continue
            results[algo][event['type']] = event_time

    return results

def get_timeline(token, date, email=None):
    endpoint = "v1/timeline/%s" % (date)
    if email:
        # Note: token needs to be uber token
        endpoint = "v1/timeline/admin/%s/%s" % (email, date)

    session = get_session(token, PROD_URL)
    if not session:
        return {}

    results = {}

    api_url = "%s%s" % (PROD_URL, endpoint)
    response = session.get(api_url, headers=HEADERS)
    data = json.loads(response.content)[0]

    if len(data) == 0:
        return {}

    if 'code' in data:
        print "Error", data
        return {}

    if not data['segments']:
        return {}

    offset_millis = data['segments'][0]['offset_millis'] / 1000
    offset_timedelta = timedelta(seconds = offset_millis)

    for event in data['segments']:
        etype = event['event_type']
        if etype in EVENT_TYPES:
            if etype == 'SLEEP' and etype in results:
                continue
            results[etype] = datetime.utcfromtimestamp(int(event['timestamp'])/1000) + offset_timedelta
    return {'WPA': results}

def get_accuracy_dict():
    accuracy = {'num': 0}
    for algo in ALGOS:
        accuracy[algo] = {}
        for dtype in DETECT_TYPES:
            accuracy[algo][dtype] = {}
            for val in EVENT_TYPES:
                accuracy[algo][dtype][val] = {
                    'num': 0, 'diff': 0, 'diff_num': 0,
                    'neg_diff': 0, 'pos_diff':0,
                    'neg_num': 0, 'pos_num': 0}
    return accuracy

def run_test(users, truths, tolerance, specific_email=None):

    now = datetime.now()
    num_days = (now - START_DAY).days

    results_fp = open("results_%s_%dmins_5.txt" % 
                (str(now)[:10], tolerance), 'w')

    results_fp.write("Run Date: %s\n" % str(now))
    # init accuracy dict
    all_accuracy = get_accuracy_dict()
    algo_better = {}

    for email in truths:
        if email not in users:
            continue;

        if specific_email is not None and email != specific_email:
            continue

        # init tracking
        accuracy = get_accuracy_dict()
        user = users[email]

        results_fp.write("Compute %s\n" % email)
        for date_string, truth in truths[email].items():
            prediction = get_prediction(user['account_id'], date_string)

            # if user['account_id'] not in PROD_HMM_ACCOUNTS:
            #     prod_results = get_timeline(ADMIN_TOKEN, date_string, email)
            #     if prod_results:
            #         prediction['WPA'] = prod_results['WPA']

            if not prediction:
                continue

            results_fp.write("%s\n" % date_string)
            for etype in EVENT_TYPES:
                actual = truth[etype]
                
                if actual == None:
                    continue
                
                res = "\t%s\tactual: %s" % (etype[:7], datetime.strftime(actual, "%m-%d %H:%M"))

                for algo in ALGOS:
                    if algo not in  prediction:
                        continue

                    res += "\t%s: " % algo
                    if etype not in prediction[algo]:
                        accuracy[algo]['missing'][etype]['num'] += 1
                        res += "None"
                        continue

                    detected = prediction[algo][etype] # detected time

                    # get time difference in minutes
                    diff = detected - actual
                    delta = divmod(diff.days * 86400 + diff.seconds, 60)
                    delta_mins = delta[0]

                    # print results
                    res += "%s\tdiff: %d " % (
                        datetime.strftime(detected, "%m-%d %H:%M"),
                        delta_mins)

                    # tally accuracy
                    if (abs(delta_mins) <= tolerance):
                        accuracy[algo]['detected'][etype]['num'] += 1;
                    else:
                        accuracy[algo]['detected'][etype]['diff'] += abs(delta_mins)
                        accuracy[algo]['detected'][etype]['diff_num'] += 1
                        if delta_mins < 0:
                            accuracy[algo]['detected'][etype]['neg_diff'] += abs(delta_mins)
                            accuracy[algo]['detected'][etype]['neg_num'] += 1
                        else:
                            accuracy[algo]['detected'][etype]['pos_diff'] += abs(delta_mins)
                            accuracy[algo]['detected'][etype]['pos_num'] += 1

                results_fp.write("%s\n" % res)
            accuracy['num'] += 1
       
        # print results for one user
        tot = accuracy['num']
        results_fp.write("\nAccuracy for %s (%d nights)\n" % (email, tot))
        if tot > 0:
            for etype in EVENT_TYPES:
                # count number of correct nights
                results_fp.write("%s\n" % etype[:7])
                acc = 0
                better = 'None'
                for algo in ALGOS:
                    data = accuracy[algo]['detected'][etype]
                    correct = data['num']
                    missing = accuracy[algo]['missing'][etype]['num']
                    res = "\t%s\tcorrect: %d, %0.1f%%\tmissing: %d, %0.1f%%\twrong: %d" % (
                        algo, correct, float(correct)/tot * 100.0,
                        missing, float(missing)/tot * 100.0,
                        tot - correct - missing)
                    accc = float(correct)/tot
                    if (accc > acc):
                        acc = float(correct)/tot
                        better = algo
                    elif accc == acc:
                        better += ', %s' % algo

                    all_accuracy[algo]['detected'][etype]['num'] += correct
                    all_accuracy[algo]['missing'][etype]['num'] += missing
                    algo_better.setdefault(email, {})
                    algo_better[email][etype] = better

                    pdiff = data['pos_diff']
                    avg_pdiff = 0.0
                    if data['pos_num']:
                        avg_pdiff = float(pdiff) / data['pos_num']

                    ndiff = data['neg_diff']
                    avg_ndiff = 0.0
                    if data['neg_num']:
                        avg_ndiff = float(ndiff) / data['neg_num']

                    avg_diff = 0.0
                    if data['diff_num']:
                        avg_diff = float(data['diff'])/data['diff_num']

                    res += "\tpredict-too-late: %d, %0.1f\ttoo-early: %d, %0.1f\taggregate: %0.1f" % (
                        data['pos_num'], avg_pdiff, data['neg_num'], avg_ndiff, avg_diff)
                    all_accuracy[algo]['detected'][etype]['pos_diff'] += data['pos_diff']
                    all_accuracy[algo]['detected'][etype]['pos_num'] += data['pos_num']
                    all_accuracy[algo]['detected'][etype]['neg_diff'] += data['neg_diff']
                    all_accuracy[algo]['detected'][etype]['neg_num'] += data['neg_num']
                    all_accuracy[algo]['detected'][etype]['diff'] += data['diff']
                    all_accuracy[algo]['detected'][etype]['diff_num'] += data['diff_num']
                    results_fp.write("%s\n" % res)

        results_fp.write("\n\n===========================================\n")
        all_accuracy['num'] += tot

    tot = all_accuracy['num']
    results_fp.write(
        "\n\nOverall_Accuracy (%d nights, accuracy-tolerance: %d mins)\n" %(
        tot, tolerance))

    if tot > 0:
        for etype in EVENT_TYPES:
            results_fp.write("%s\n" % etype[:7])
            for algo in ALGOS:
                data = all_accuracy[algo]['detected'][etype]
                correct = data['num']
                missing = all_accuracy[algo]['missing'][etype]['num']

                res = "\t%s\tcorrect: %d, %0.1f%%\tmissing: %d, %0.1f%%\twrong: %d" % (
                    algo[:3], correct, float(correct)/tot * 100.0,
                    missing, float(missing)/tot * 100.0,
                    tot - correct - missing)

                pdiff = data['pos_diff']
                avg_pdiff = 0.0
                if data['pos_num']:
                    avg_pdiff = float(pdiff) / data['pos_num']

                ndiff = data['neg_diff']
                avg_ndiff = 0.0
                if data['neg_num']:
                    avg_ndiff = float(ndiff) / data['neg_num']

                avg_diff = 0.0
                if data['diff_num']:
                    avg_diff = float(data['diff']) / data['diff_num']

                res += "\tpredict-too-late: %d, %0.1f\ttoo-early: %d, %0.1f\taggregate: %0.1f" % (
                    data['pos_num'], avg_pdiff, data['neg_num'], avg_ndiff, avg_diff)
                results_fp.write("%s\n" % res)

            results_fp.write("\n")

        results_fp.write("\nBetter algorithm\n")
        algo_users = {}
        for email in algo_better:
            results_fp.write("%s\t%r\n" % (email, algo_better[email]))
            for etype, algo in algo_better[email].items():
                algo_users.setdefault(etype, {})
                algo_users[etype].setdefault(algo, 0)
                algo_users[etype][algo] += 1

        results_fp.write("\nBetter algorithm by users\n")
        for etype in algo_users:
            tot = sum(algo_users[etype].values())
            results_fp.write("%s" % etype[:7])
            for algo, val in algo_users[etype].items():
                results_fp.write("\t%s: %d, %0.1f" % (
                                algo, val, float(val)/tot * 100.0))
            results_fp.write("\n")
        results_fp.write("\n")

def main(filename, token_filename, tolerance, specific_email=None):
    users = read_user_tokens(token_filename)
    truths = read_truths(filename)
    run_test(users, truths, tolerance, specific_email)

if __name__ == '__main__':
    if len(sys.argv) < 4:
        print "usage: python compare_prod_timeline.py token_file truth_file accuracy_tolerance"
        sys.exit()
    token_filename = sys.argv[1]
    filename = sys.argv[2]
    tolerance = int(sys.argv[3])
    email = None
    if len(sys.argv) == 5:
        email = sys.argv[4]
    main(filename, token_filename, tolerance, email)
