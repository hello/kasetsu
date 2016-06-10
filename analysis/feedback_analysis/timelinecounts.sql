SELECT date_of_night,COUNT(*) FROM timeline_analytics WHERE error=0 GROUP BY date_of_night ORDER BY date_of_night;
