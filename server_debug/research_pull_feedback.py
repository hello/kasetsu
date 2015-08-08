#!/usr/bin/python
import datetime
import calendar
import requests
import copy
import csv
import os

k_url = 'https://research-api-benjo.hello.is/v1/datascience/feedbackutc/{}'
k_magic_auth = os.environ['RESEARCH_TOKEN']
k_headers = {'Authorization' : 'Bearer %s' % k_magic_auth}

k_accounts_list = [1006,1056,1215,1398,1848,15116,15487,15488,15489,15517,15539,15545,15599,15777,15877,15888,16077,16086,16127,16137,16209,16256,16307,16329,16359,16517,16695,17029,17096,17105,17109,17139,17156,17166,17239,17245,17308,17328,17339,17347,17465,17468,17486,17488,17538,17575,17586,17627,17687,17867,17878,17959,18015,18057,18177,18209,18559,18577,18619,18636,18666,18669,18749,18768,18916,18926,19006,19219,19229,19276,19287,19298,19308,19516,19648,19915,19968,20019,20086,20128,20275,20305,20316,20379,20535,20589,20619,20667,20698,20767,20828,20835,20866,20879,20987,20996,21007,21017,21038,21046,21047,21065,21069,21075,21125,21158,21168,21187,21289,21319,21355,21409,21496,21579,21627,21628,21638,21669,21679,21709,21736,21745,21798,21825,21936,21986,21996,22155,22177,22187,22266,22375,22627,22646,22729,22787,22797,22808,22817,22866,22886,22926,22987,23028,23077,23085,23107,23116,23138,23226,23247,23249,23286,23425,23427,23429,23548,23576,23747,23749,23827,23848,23927,24006,24206,24225,24335,24357,24368,24437,24457,24519,24526,24576,24839,24958,24978,25046,25098,25168,25406,25425,25426,25428,25435,25436,25447,25555,25685,25707,25798,25836,25837,25879,25908,25976,25977,25985,26026,26095,26097,26119,26275,26369,26417,26425,26448,26548,26755,26795,26827,26885,26889,26918,26936,27055,27097,27135,27208,27389,27437,27545,27548,27639,27718,27768,27835,27885,28058,28097,28125,28156,28229,28275,28445,28465,28478,28487,28565,28608,28626,28639,28649,28676,28708,28749,28807,28858,29116,29186,29257,29326,29365,29387,29488,29498,29568,29625,29655,29687,29706,29766,29769,29777,29779,29858,29868,29899,29938,29957,29977,29988,30016,30055,30058,30067,30068,30086,30089,30105,30125,30145,30188,30219,30248,30255,30259,30268,30326,30365,30386,30389,30395,30416,30425,30426,30427,30458,30469,30557,30586,30607,30648,30666,30678,30699,30717,30718,30766,30879,30909,31018,31048,31056,31065,31077,31088,31127,31177,31196,31198,31199,31205,31208,31246,31276,31277,31316,31339,31357,31429,31458,31476,31487,31495,31496,31505,31539,31557,31565,31589,31686,31687,31748,31755,31766,31797,31808,31817,31826,31866,31889,31937,31949,32045,32065,32085,32166,32189,32195,32267,32366,32398,32428,32438,32455,32456,32476,32478,32497,32539,32585,32639,32655,32685,32686,32718,32719,32775,32806,32815,32848,32858,32907,32917,32945,32968,32976,33036,33045,33067,33075,33079,33129,33145,33169,33176,33177,33187,33188,33199,33227,33228,33237,33238,33248,33298,33299,33315,33347,33369,33417,33475,33537,33649,33656,33736,33768,33818,33837,33838,33845,33857,33866,33868,33876,33877,33906,33949,33995,34018,34048,34049,34097,34117,34157,34176,34195,34205,34206,34229,34328,34357,34365,34368,34405,34408,34439,34475,34509,34526,34527,34589,34625,34639,34647,34708,34747,34755,34786,34797,34809,34817,34825,34849,34855,34878,34919,34927,35038,35085,35086,35095,35096,35127,35176,35195,35219,35269,35309,35335,35339,35346,35347,35385,35505,35518,35546,35565,35587,35605,35615,35637,35638,35658,35667,35676,35698,35788,35806,35846,35847,35868,35979,35995,36045,36047,36076,36109,36199,36208,36225,36226,36327,36337,36397,36415,36425,36537,36587,36595,36609,36666,36717,36719,36767,36798,36817,36855,36907,36917,36948,36965,36967,36999,37036,37045,37057]

#k_accounts_list = [1062,1180,1190,1610,1912,15472,15594,15611,15651,15913,15983,15991,16014,16020,16023,16024,16214,16283,16554,16560,16622,16840,16893,16894,16941,16950,16954,17063,17093,17194,17210,17344,17370,17413,17424,17450,17542,17591,17683,17713,17794,17851,17911,17994,18002,18004,18032,18091,18120,18160,18164,18210,18224,18240,18241,18301,18362,18404,18430,18463,18493,18583,18602,18672,18852,18990,19090,19140,19152,19170,19301,19304,19324,19340,19374,19500,19701,19734,20000,20050,20080,20110,20153,20170,20270,20402,20404,20583,20741,20744,20751,20802,20833,20841,20854,20892,20954,20961,20962,20990,21032,21062,21110,21150,21171,21252,21253,21261,21263,21273,21281,21300,21312,21374,21494,21542,21543,21561,21570,21622,21653,21673,21701,21723,21823,21874,21911,21930,21952,21961,21962,22001,22062,22110,22133,22153,22284,22314,22354,22362,22413,22414,22514,22541,22551,22554,22642,22821,22862,23013,23063,23083,23113,23124,23241,23293,23340,23341,23354,23393,23400,23401,23490,23604,23643,23680,23694,23712,23721,23754,23810,23913,24022,24081,24211,24222,24414,24451,24520,24533,24552,24562,24603,24612,24731,24732,24744,24784,24793,24811,24941,24971,25004,25024,25030,25070,25094,25111,25153,25172,25224,25272,25342,25422,25444,25452,25462,25522,25551,25582,25643,25661,25691,25811,25854,25864,25870,25872,25892,25971,26012,26024,26030,26044,26063,26102,26103,26180,26190,26281,26292,26351,26421,26424,26450,26522,26581,26663,26824,27144,27193,27321,27392,27420,27442,27490,27504,27601,27681,27700,27764,27882,27904,28024,28063,28112,28154,28211,28271,28451,28464,28741,28813,28901,28913,29073,29124,29162,29172,29211,29292,29362,29364,29431,29433,29530,29571,29572,29583,29610,29641,29643,29660,29672,29693,29700,29702,29704,29714,29732,29783,29824,29832,29834,29844,29850,29851,29871,29892,29910,29920,29922,29931,29933,29944,29981,30001,30002,30003,30021,30033,30051,30073,30074,30080,30081,30111,30133,30210,30213,30231,30253,30273,30313,30322,30334,30350,30383,30444,30462,30474,30541,30564,30570,30574,30590,30594,30672,30704,30710,30711,30731,30734,30773,30774,30790,30793,30802,30831,30832,30853,30871,30872,30892,30893,30910,30914,30920,30964,30980,30993,31091,31112,31131,31141,31192,31220,31242,31250,31252,31340,31381,31392,31403,31442,31443,31444,31462,31524,31572,31581,31613,31631,31652,31661,31683,31703,31704,31760,31762,31770,31801,31813,31814,31821,31824,31830,31913,31924,31972,31991,32030,32034,32071,32112,32140,32160,32183,32274,32324,32342,32391,32414,32431,32502,32520,32544,32594,32664,32673,32682,32812,32814,32820,32823,32900,32902,32934,32973,33032,33063,33072,33073,33181,33191,33234,33261,33272,33274,33310,33333,33340,33341,33350,33351,33354,33402,33403,33430,33461,33513,33522,33561,33602,33612,33650,33702,33774,33861,33872,33873,33992,34092,34124,34152,34160,34192,34200,34203,34212,34233,34374,34392,34402,34414,34480,34503,34592,34653,34673,34710,34711,34712,34722,34791,34920,34973,35043,35083,35084,35094,35134,35160,35243,35270,35273,35320,35334,35342,35390,35500,35503,35504,35531,35580,35583,35590,35641,35664,35680,35682,35702,35704,35743,35760,35801,35833,35843,35974,35992,36011,36020,36061,36103,36191,36194,36203,36211,36220,36221,36223,36232,36240,36241,36244,36251,36260,36293,36294,36302,36334,36370,36374,36384,36401,36403,36481,36493,36502,36513,36544,36552,36554,36584,36591,36593,36594,36623,36704,36732,36741,36744,36762,36790,36814,36854,36880,36900,36961,37021,37040,37044]

k_min_date = '2015-07-30'
k_event_type = 'OUT_OF_BED'

def pull_data(account_id):
    responses = []
    
    params = {'min_date' : k_min_date}
    url = k_url.format(account_id)
    print url
    response = requests.get(url,params=params,headers=k_headers)
        
    if not response.ok:
        print 'fail with %d on %s ' % (response.status_code,'foo')
        return []

    data = response.json()
        
    return data
       
def process_data(data,threshold,event_type):
    complaint_count = 0
    
    for item in data:
        if event_type != None and event_type != item['event_type']:
            continue

        delta = item['new_time_utc'] - item['old_time_utc']
        delta /= 60000

        if abs(delta) > threshold:
            complaint_count += 1

    return complaint_count
        
if __name__ == '__main__':
    complaint_count = 0
    
    for account_id in k_accounts_list:
        data = pull_data(account_id)
        c = process_data(data,20,k_event_type)
        complaint_count +=  c

    print complaint_count
 

