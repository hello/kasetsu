#!/usr/bin/python
import psycopg2
import os
import datetime
import time

all_groups = [54624,30021,48543,45502,42126,45234,41639,35744,46707,31743,37381,49991,21468,16024,31695,38082,31231,51012,20809,47478,53179,55606,21001,41288,25864,45943,20859,48154,33168,37955,47114,50512,54251,17097,53834,19123,32793,19182,26667,40818,45024,33861,51413,54057,40737,19920,48530,53796,28084,21747,54871,20441,26099,50524,30085,52173,30586,15163,29388,44132,40558,22551,25516,25582,30867,30118,44549,31094,17166,46390,33254,30140,35467,30221,44208,49978,35100,34432,55151,24675,16131,54669,29772,24291,35447,32158,40017,36583,35912,55935,50037,54417,23028,52496,36855,45336,30344,47721,50969,30427,30472,54326,29703,53780,51573,46150,53691,55815,49035,23615,18020,51193,43534,55193,54318,32555,48035,48971,50586,16971,28824,49192,21201,30592,49906,35851,53244,45791,36435,38867,52568,37372,52133,34722,1839,30802,30358,17465,37820,32413,33494,39294,51315,53019,25054,55994,52507,45549,19008,46739,19215,21605,1161,49590,15880,41773,50724,31199,48334,15281,51073,21798,53848,23996,29569,41687,24982,30425,44015,24335,30510,48551,50105,49121,46635,38514,35083,48599,51924,26746,49566,35419,55206,34320,39167,21986,45122,25094,19734,42528,34389,38594,47680,48564,46808,53446,33914,49626,48433,30351,29680,23713,52448,16215,30677,41848,52881,38834,44420,33709,33868,36241,43862,17867,17714,29347,25085,48967,17286,39174,15070,21150,53032,50509,29948,34827,34592,18566,23043,23257,39595,35739,32015,30669,34189,47116,47140,15218,27975,34753,49239,18674,15891,49981,29610,49541,39872,20179,32064,39922,52518,28559,55192,44291,54176,34128,31466,45346,33227,19914,41892,50726,54895,27730,37590,36982,20357,47871,23624,44252,22500,44852,19842,15159,22644,20024,49218,15086,34122,50357,31020,40902,30992,19219,29364,1465,22116,35780,55019,50447,52100,51037,49292,39225,20915,38675,25098,46242,38385,44339,23068,16017,15983,38749,47414,37781,18815,19217,33581,15569,49452,21079,29656,15854,31428,42859,47105,47204,30978,36010,27504,52745,45701,34751,33199,31003,30590,17903,50826,32493,54852,55100,51933,17314,48374,21899,15357,19665,55432,49226,25179,28629,52107,34472,20875,27067,26497,29761,25976,30259,37976,55346,21854,35141,45990,49745,26026,36230,1508,45642,28345,29682,39400,40736,49431,26971,27601,55602,49732,51670,43142,44977,54711,50525,51516,48116,22078,26632,17463,22164,15249,53431,34928,50579,48405,30909,18943,52176,44214,26424,45242,44720,51394,54672,27105,48587,21452,42353,26795,16093,33075,26544,29641,32700,29828,46649,25579,41239,53023,49116,54550,25320,31367,20672,48920,16802,49858,29802,49888,37758,27256,43496,34151,50562,32305,33873,51451,17245,55055,54571,1479,20780,54133,32847,26634,45774,52548,26082,52086,48798,55164,40541,33007,38635,53962,52047,16739,46181,51872,34834,54323,19600,55139,55053,46183,48491,52106,41859,17687,35647,36384,37157,17446,39498,17435,24003,47946,29888,30255,54102,47430,45595,41809,55161,55382,42284,49147,37682,44971,29833,48659,39204,35160,19447,50753,50540,52474,47895,44393,48495,31047,49562,33138,50155,22421,29922,41425,25416,39238,39014]

def main():
    conn = psycopg2.connect("dbname='common' user='common' host='common-replica-1.cdawj8qazvva.us-east-1.rds.amazonaws.com' port=5432 password='hello-common'")
    f = open('get_group_complaint_count.str','r')
    query_str = f.read()
    f.close()


    ag = ','.join([str(a) for a in all_groups ])

    a_query = query_str.format('5',ag)
    b_query = query_str.format('4',ag)
    cur = conn.cursor()

    print '\n\n------A GROUP---------'
    cur.execute(a_query)
    for record in cur:
        print record

    print '\n\n------B GROUP---------'
    cur.execute(b_query)
    for record in cur:
        print record

if __name__=='__main__':
    main()

