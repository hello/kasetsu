(SELECT q3.event_type,SUM((abs(q3.corrected_time) > 30)::int) as counts, SUM((abs(q3.corrected_time) > 30)::int)::float / COUNT(*) as frac,AVG(q3.corrected_time),STDDEV_SAMP(q3.corrected_time) 
  FROM
  (SELECT id,q2.account_id,q2.date_of_night,q2.event_type,q2.created,
  CASE
    WHEN timediff > 720 then timediff - 1440
    WHEN timediff < -720 then 1440 + timediff
    ELSE timediff
  END AS corrected_time
  FROM
    (SELECT q1.id,q1.account_id,q1.date_of_night,q1.event_type,q1.created,(extract(epoch FROM t2) - extract(epoch FROM t1))/60 timediff FROM
      (SELECT id,account_id,date_of_night,event_type,created,
          to_timestamp(concat('1970-01-01 ',new_time),'YYY-MM-DD HH24:mi')::timestamp without time zone t2,
          to_timestamp(concat('1970-01-01 ',old_time),'YYY-MM-DD HH24:mi')::timestamp without time  zone t1
       FROM timeline_feedback
       WHERE event_type IN (11,12,13,14)
      ) q1
    ) q2 
  ) q3
WHERE 
q3.created >= '2016-04-21 22:35:00' 
AND 
q3.date_of_night >= '2016-04-21'
AND q3.account_id IN
(30590,38594,47114,30677,23615,29641,23028,50509,43862,34128,17097,24982,1479,54417,39595,41288,18674,47680,49192,21605,17867,55151,36855,33861,20672,49906,16739,34722,47105,25416,44291,33494,53796,51573,38514,46242,48334,20809,21747,26632,55100,50826,31003,49745,26795,55192,47116,25976,34151,40818,30118,54102,40017,50540,33254,37682,44015,52106,34432,47478,52881,22078,31020,19123,15569,54624,33168,51933,54852,53019,46635,50586,50753,43142,19217,55815,52086,23713,35447,35083,21468,35780,32555,47414,54669,26544,15983,44420,27601,21079,46390,44393,20859,37976,30255,29948,50525,48405,30592,30425,32847,15854,36583,33873,41892,34189,19842,53780,46150,55193,52100,29888,50512,39167,15070,48599,40558,41859,42859,19182,39872,51012,31047,16024,46181,21001,18566,32305,51451,53431,22551,16131,22164,32413,29364,51924,39498,34389,33227,50969,54571,54176,45595,33914,19219,19447,29680,21201,37372,48495,28559,31231,35744,30867,51193,31743,21986,36435,19734,45024,36241,34592,49239,29347,17245,44720,45234,36384,48971,30669,53032,48530,52176,17435,52047,48920,41848,46808,29682,49292,53691,27256,45549,26082,25085,46707,35739,33581,49590,48564,38867,31199,55161,17446,23996,25579,39294,26026,54672,45990,45346,30427,47204,31367,54057,45336,45242,50724,24675,26634,34928,51872,49978,55994,1508,15163,53446,45943,49147,44208,20441,30344,55164,28084,49035,30472,15218,36230,15880,38834,50155,15281,44252,16971,42284,54326,35160,33709,45642,48798,55935,34320,32700,32064,34834,43534,50524,52507,40737,29772)
GROUP BY q3.event_type
ORDER BY q3.event_type);
