--run this on redshit
--SELECT date_trunc('day', ts) AS dd, COUNT(DISTINCT account_id) FROM tracker_motion_master WHERE ts > '2015-03-01' GROUP BY dd ORDER BY dd ASC;
SELECT date_trunc('day', ts) AS dd, COUNT(DISTINCT account_id) FROM device_sensors_master WHERE ts > '2015-03-01' GROUP BY dd ORDER BY dd ASC;
