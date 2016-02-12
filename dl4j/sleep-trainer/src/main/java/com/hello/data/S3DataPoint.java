package com.hello.data;

import com.google.common.base.Optional;
import org.joda.time.DateTime;
import org.joda.time.DateTimeZone;
import org.joda.time.format.DateTimeFormat;
import org.joda.time.format.DateTimeFormatter;

/**
 * Created by benjo on 2/11/16.
 */
//accountid, date/time, ambient_light,ambient_light_variance,wave_count,audio_num_disturbances,audio_peak_disturbances_db, my pill durations, partner pill duration
public class S3DataPoint {
    final public double [] x;
    final public long accountId;
    final public long time;

    public static Optional<S3DataPoint> create(final String line) {

        final String [] items = line.split(",");

        if (items.length < 9) {
            return Optional.absent();
        }

        final long accountId = Long.valueOf(items[0]);
        final DateTimeFormatter dateTimeFormatter = DateTimeFormat.forPattern("yyyy-MM-dd HH:mm:ss").withZone(DateTimeZone.UTC);

        final DateTime dateTime = dateTimeFormatter.parseDateTime(items[1]);


        final double [] x = new double[7];
        for (int i = 2; i < 9; i++) {
            x[i-2] = Double.valueOf(items[i]);
        }

        return Optional.of(new S3DataPoint(x,accountId,dateTime.withZone(DateTimeZone.UTC).getMillis()));
    }

    private S3DataPoint(double[] x, long accountId, final long time) {
        this.x = x;
        this.accountId = accountId;
        this.time = time;
    }
}
