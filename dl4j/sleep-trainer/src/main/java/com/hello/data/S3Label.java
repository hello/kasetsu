package com.hello.data;

import com.google.common.base.Optional;
import org.joda.time.DateTime;
import org.joda.time.DateTimeZone;
import org.joda.time.format.DateTimeFormat;
import org.joda.time.format.DateTimeFormatter;

/**
 * Created by benjo on 2/11/16.
 */
public class S3Label {

    private static DateTime getDateOfMorningEvents(final DateTime dateOfNight, final String hhmm) {
        final String [] hhmms = hhmm.split(":");
        final int hour = Integer.valueOf(hhmms[0]);
        final int minute = Integer.valueOf(hhmms[1]);

        DateTime time = dateOfNight.plusHours(hour).plusMinutes(minute);
        if (hour < 16) {
            time = time.plusDays(1);
        }

        return time;
    }


    private S3Label(DateTime t1, DateTime t2, long accountId, DateTime evening) {
        this.t1 = t1;
        this.t2 = t2;
        this.accountId = accountId;
        this.evening = evening;
    }

    public final DateTime t1;
    public final DateTime t2;
    public final long accountId;
    public final DateTime evening;

    public static Optional<S3Label> create(final String line) {
        final String [] items = line.split(",");

        if (items.length < 4) {
            return Optional.absent();
        }

        final long accountId = Long.valueOf(items[0]);
        final DateTimeFormatter dateTimeFormatter = DateTimeFormat.forPattern("yyyy-MM-dd HH:mm:ss").withZone(DateTimeZone.UTC);

        final DateTime dateOfNight = dateTimeFormatter.parseDateTime(items[1]);

        final DateTime t1 = getDateOfMorningEvents(dateOfNight,items[2]);
        final DateTime t2 = getDateOfMorningEvents(dateOfNight,items[3]);

        return Optional.of(new S3Label(t1,t2,accountId,dateOfNight));

    }

    public int getLabel(final long time) {
        return getLabel(new DateTime(time,DateTimeZone.UTC));
    }

    public int getLabel(final DateTime time) {
        final int c1 = t1.compareTo(time);
        final int c2 = t2.compareTo(time);

        if (c1 == 1 && c2 == -1) {
            return 1;
        }

        return 0;
    }
}