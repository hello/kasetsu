--run this on common replica
(SELECT date_of_night,count(*) 
 FROM
     (SELECT id,q2.account_id,q2.date_of_night,q2.event_type,case 
         WHEN timediff > 720 then timediff - 1440
     WHEN timediff < -720 then 1440 + timediff
         ELSE timediff
     END AS corrected_time
         FROM
         (SELECT q1.id,q1.account_id,q1.date_of_night,q1.event_type,(extract(epoch from t2) - extract(epoch from t1))/60 timediff 
         FROM
             (SELECT id,account_id,date_of_night,event_type,
     to_timestamp(concat('1970-01-01 ',new_time),'YYY-MM-DD HH24:mi')::timestamp without time zone t2,
     to_timestamp(concat('1970-01-01 ',old_time),'YYY-MM-DD HH24:mi')::timestamp without time  zone t1
                 FROM 
                 timeline_feedback WHERE date_of_night >= '2015-03-01' AND event_type=12
             ) q1
             ) q2 
        ) q3

WHERE ABS(corrected_time) > 30
GROUP BY date_of_night
ORDER BY date_of_night ASC
);
