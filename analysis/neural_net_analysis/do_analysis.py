#!/usr/bin/python
import psycopg2
import os
import datetime
import time

A_group = [30590,38594,47114,30677,23615,29641,23028,50509,43862,34128,17097,24982,1479,54417,39595,41288,18674,47680,49192,21605,17867,55151,36855,33861,20672,49906,16739,34722,47105,25416,44291,33494,53796,51573,38514,46242,48334,20809,21747,26632,55100,50826,31003,49745,26795,55192,47116,25976,34151,40818,30118,54102,40017,50540,33254,37682,44015,52106,34432,47478,52881,22078,31020,19123,15569,54624,33168,51933,54852,53019,46635,50586,50753,43142,19217,55815,52086,23713,35447,35083,21468,35780,32555,47414,54669,26544,15983,44420,27601,21079,46390,44393,20859,37976,30255,29948,50525,48405,30592,30425,32847,15854,36583,33873,41892,34189,19842,53780,46150,55193,52100,29888,50512,39167,15070,48599,40558,41859,42859,19182,39872,51012,31047,16024,46181,21001,18566,32305,51451,53431,22551,16131,22164,32413,29364,51924,39498,34389,33227,50969,54571,54176,45595,33914,19219,19447,29680,21201,37372,48495,28559,31231,35744,30867,51193,31743,21986,36435,19734,45024,36241,34592,49239,29347,17245,44720,45234,36384,48971,30669,53032,48530,52176,17435,52047,48920,41848,46808,29682,49292,53691,27256,45549,26082,25085,46707,35739,33581,49590,48564,38867,31199,55161,17446,23996,25579,39294,26026,54672,45990,45346,30427,47204,31367,54057,45336,45242,50724,24675,26634,34928,51872,49978,55994,1508,15163,53446,45943,49147,44208,20441,30344,55164,28084,49035,30472,15218,36230,15880,38834,50155,15281,44252,16971,42284,54326,35160,33709,45642,48798,55935,34320,32700,32064,34834,43534,50524,52507,40737,29772]

B_group = [51315,45701,22644,32793,33007,25864,24335,26099,24003,27975,18815,49218,35419,44971,17465,16017,17166,39174,17687,38385,50579,27105,33138,42528,50726,41773,38635,44214,17714,55346,22421,48116,25582,52133,50562,33075,51413,22500,39204,47946,26667,33868,52548,21150,30992,26424,49626,30358,49452,35912,39238,47140,29802,48433,35647,55019,49541,53023,47430,53179,54871,48374,21854,52568,38675,34827,49981,41425,50447,30259,20179,31428,23257,15086,32015,36010,16802,46649,21452,35467,34751,52518,37590,17903,45791,39014,21798,52107,25516,29703,20915,48587,37758,45122,51037,18943,51073,49566,28824,46739,40541,31466,44132,34753,53244,15249,29388,19215,48491,42353,41809,47871,19914,25179,1161,49431,30510,29922,23043,51670,26971,17314,49562,17286,48551,15357,27067,30351,26746,1465,20357,38749,29569,38082,28629,50037,21899,40902,30021,32158,55055,30978,30221,29761,49121,44549,20024,37820,29656,45774,50105,28345,41639,51516,20780,19665,55432,39400,55602,23068,49116,37955,39922,26497,55606,34472,19008,52745,34122,25320,29610,33199,49732,25098,27730,43496,51394,16215,52474,29833,50357,54711,48543,22116,54251,54323,47721,48659,54133,52448,30586,37381,30909,55139,30802,49991,31094,23624,19920,54550,18020,36982,54895,25094,45502,35100,44852,1839,27504,35851,41687,48035,52173,49226,25054,44977,32493,16093,15891,39225,55053,49888,30140,53848,42126,49858,24291,53962,54318,52496,30085,40736,41239,48154,48967,37157,15159,35141,20875,55206,29828,17463,47895,37781,31695,53834,44339,19600,46183,55382]

def main():
    conn = psycopg2.connect("dbname='common' user='common' host='common-replica-1.cdawj8qazvva.us-east-1.rds.amazonaws.com' port=5432 password='hello-common'")
    f = open('get_group_complaint_count.str','r')
    query_str = f.read()
    f.close()


    ag = ','.join([str(a) for a in A_group ])
    bg = ','.join([str(b) for b in B_group ])

    a_query = query_str.format(ag)
    b_query = query_str.format(bg)
    cur = conn.cursor()

    cur.execute(a_query)
    for record in cur:
        print record

    cur.execute(b_query)
    for record in cur:
        print record

if __name__=='__main__':
    main()


