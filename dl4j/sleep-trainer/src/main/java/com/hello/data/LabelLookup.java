package com.hello.data;

import com.google.common.base.Optional;
import com.google.common.collect.ArrayListMultimap;
import org.joda.time.DateTime;

import java.util.List;

/**
 * Created by benjo on 2/11/16.
 */
public class LabelLookup {
    ArrayListMultimap<Long,S3Label> labels;


    public static LabelLookup create(final List<S3Label> labelsList) {
        ArrayListMultimap<Long,S3Label> labels = ArrayListMultimap.create();

        for (final S3Label label : labelsList) {
            labels.put(label.accountId,label);
        }

        return new LabelLookup(labels);

    }

    private LabelLookup(final ArrayListMultimap<Long,S3Label> labels) {
        this.labels = labels;
    }

    public Optional<Integer> getLabel(final long accountId, final long time) {

        if (!labels.containsKey(accountId)) {
            return Optional.absent();
        }

        final List<S3Label> labelList = labels.get(accountId);

        for (final S3Label label : labelList) {
            if (label.getLabel(time) == 1) {
                return Optional.of(new Integer(1));
            }
        }

        return Optional.of(new Integer(0));
    }
}
