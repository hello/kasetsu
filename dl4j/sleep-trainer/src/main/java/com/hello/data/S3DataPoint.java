package com.hello.data;

import com.google.common.base.Optional;
import org.joda.time.DateTime;
import org.joda.time.DateTimeZone;
import org.joda.time.format.DateTimeFormat;
import org.joda.time.format.DateTimeFormatter;

/**
 * Created by benjo on 2/11/16.
 */
//accountid, date/time,
// [0] ambient_light
// [1] ambient_light_variance,
// [2] wave_count,
// [3] audio_num_disturbances,
// [4] audio_peak_disturbances_db,
// [5] my pill durations,
// [6] partner pill duration
// [7] pill pagnitude
public class S3DataPoint implements Comparable<S3DataPoint> {
    final public double [] x;
    final public long accountId;
    final public long time;

    private static final int EXEPCTED_NUM_COLS = 10;

    @Override
    public int compareTo(final S3DataPoint o) {
        if (time > o.time) {
            return 1;
        }

        if (time < o.time) {
            return -1;
        }

        return 0;
    }

    enum Transform {
        IDENTITY,
        LOG2,
        SQRT
    };

    private final static double [] CONVERSION_FACTORS = {0.003814697265625, 1.4551915228366852e-05,1.0,1.0,0.00009765625,1.0,1.0,1.0 / 1000.};
    private final static double [] OFFSETS = {1.0,1.0,0.0,1.0,-4.0,0.0,0.0,0.0};
    private final static Transform [] TRANSFORMS = {Transform.LOG2,Transform.LOG2,Transform.IDENTITY,Transform.LOG2,Transform.IDENTITY,Transform.IDENTITY,Transform.IDENTITY,Transform.IDENTITY};

    private static double [] applyTransform(final double [] x ) {
        final double [] y = new double[x.length];

        for (int i = 0; i < x.length; i++) {
            y[i] = x[i] * CONVERSION_FACTORS[i] + OFFSETS[i];

            if (TRANSFORMS[i].equals(Transform.LOG2)) {
                y[i] = Math.log(y[i]) / Math.log(2.0);
            }
            else  if (TRANSFORMS[i].equals(Transform.SQRT)) {
                if (y[i] < 0.0) {
                    y[i] = 0.0;
                }

                y[i] = Math.sqrt(y[i]);
            }

            if (Double.isNaN(y[i])) {
                y[i] = 0.0;
            }

            if (y[i] < 0.0) {
                y[i] = 0.0;
            }
        }

        return y;
    }

    public static Optional<S3DataPoint> create(final String line) {

        final String [] items = line.split(",");

        if (items.length < EXEPCTED_NUM_COLS) {
            return Optional.absent();
        }

        final long accountId = Long.valueOf(items[0]);
        final DateTimeFormatter dateTimeFormatter = DateTimeFormat.forPattern("yyyy-MM-dd HH:mm:ss").withZone(DateTimeZone.UTC);

        final DateTime dateTime = dateTimeFormatter.parseDateTime(items[1]);


        final double [] x = new double[EXEPCTED_NUM_COLS - 2];
        for (int i = 2; i < EXEPCTED_NUM_COLS; i++) {
            x[i-2] = Double.valueOf(items[i]);
        }

        return Optional.of(new S3DataPoint(applyTransform(x),accountId,dateTime.withZone(DateTimeZone.UTC).getMillis()));
    }

    private S3DataPoint(double[] x, long accountId, final long time) {
        this.x = x;
        this.accountId = accountId;
        this.time = time;
    }
}
