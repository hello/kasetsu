package com.hello.data;

import com.amazonaws.ClientConfiguration;
import com.amazonaws.auth.AWSCredentialsProvider;
import com.amazonaws.auth.DefaultAWSCredentialsProviderChain;
import com.amazonaws.services.s3.AmazonS3;
import com.amazonaws.services.s3.AmazonS3Client;
import com.amazonaws.services.s3.model.GetObjectRequest;
import com.amazonaws.services.s3.model.S3Object;
import com.clearspring.analytics.util.Lists;
import com.google.common.base.Optional;
import com.google.common.io.CharStreams;
import org.joda.time.DateTimeConstants;
import org.nd4j.linalg.api.ndarray.INDArray;
import org.nd4j.linalg.dataset.DataSet;
import org.nd4j.linalg.factory.Nd4j;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.io.IOException;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.util.Collections;
import java.util.List;
import java.util.Scanner;
import java.util.zip.GZIPInputStream;

/**
 * Created by benjo on 2/10/16.
 */
public class S3SleepDataSource {
    final static Logger LOGGER = LoggerFactory.getLogger(S3SleepDataSource.class);
    final static int NUM_LABELS = 2;
    final static int MAX_GAP_SIZE = 5;

    final int numInputs;
    final int numOutputs;
    private final List<DataSet> dataSets;

    private static Optional<DataSet> createDataSet(final LabelLookup lookup, final List<S3DataPoint> oneDaysData, final int numMinutes) {
        final int numFeats = oneDaysData.get(0).x.length;
        final INDArray labels = Nd4j.zeros(new int[]{1,NUM_LABELS,numMinutes + 1});
        final INDArray features = Nd4j.zeros(new int[]{1,numFeats,numMinutes + 1});
        final INDArray mat = features.slice(0);

        final long t0 = oneDaysData.get(0).time;
        int lastidx = -1;
        for (final S3DataPoint p : oneDaysData) {
            final int idx = (int) ((p.time - t0) / (long)DateTimeConstants.MILLIS_PER_MINUTE);

            final int gap = idx - lastidx;

            if (gap == 0) {
                //dup
                continue;
            }

            if (gap > 1) {
                int foo = 3;
                foo++;
            }

            int startIdx = lastidx + 1;
            final int endIdx = idx;

            if (gap > MAX_GAP_SIZE) {
                return Optional.absent();
            }




            for (int localIdx = startIdx; localIdx <= endIdx; localIdx++) {
                final INDArray vec = Nd4j.create(p.x).reshape(numFeats, 1);
                mat.putColumn(idx, vec);

                final Optional<Integer> label = lookup.getLabel(p.accountId, p.time);

                if (label.isPresent()) {
                    labels.putScalar(new int[]{0, label.get(), idx}, 1.0);
                }
            }

            lastidx = idx;
        }


       return Optional.of(new DataSet(features,labels));


    }

    public static S3SleepDataSource create(final String bucket, final String [] datakeys, final String[] labelkeys) {
        final List<List<S3DataPoint>> allData = Lists.newArrayList();
        /* GET RAW DATA  */

        final AWSCredentialsProvider awsCredentialsProvider= new DefaultAWSCredentialsProviderChain();
        final ClientConfiguration clientConfiguration = new ClientConfiguration();
        final AmazonS3 amazonS3 = new AmazonS3Client(awsCredentialsProvider, clientConfiguration);

        String csvdata = "";
        for (final String key : datakeys) {
            final String data = S3Utils.getZippedS3Object(amazonS3,bucket,key);

            long lastAccountId = -1;
            List<S3DataPoint> dpList = Lists.newArrayList();
            Scanner scanner = new Scanner(data);
            while (scanner.hasNextLine()) {
                final Optional<S3DataPoint> dpOptional = S3DataPoint.create(scanner.nextLine());

                if (!dpOptional.isPresent()) {
                    continue;
                }

                final S3DataPoint dp = dpOptional.get();

                if (dp.accountId != lastAccountId) {
                    if (!dpList.isEmpty()) {
                        allData.add(dpList);
                    }
                    dpList = Lists.newArrayList();
                }

                dpList.add(dp);
                lastAccountId = dp.accountId;


            }
            scanner.close();


        }

        /*  GET LABELS  */
        final List<S3Label> labelList = Lists.newArrayList();

        for (final String key : labelkeys) {
            final String [] filebits = key.split("\\.");
            String data = "";
            if (filebits[filebits.length - 1].equals("gz")) {
                data = S3Utils.getZippedS3Object(amazonS3,bucket,key);
            }
            else {
                data = S3Utils.getRegularS3Object(amazonS3,bucket,key);
            }

            Scanner scanner = new Scanner(data);
            while (scanner.hasNextLine()) {
                final Optional<S3Label> label = S3Label.create(scanner.nextLine());

                if (!label.isPresent()) {
                    continue;
                }

                labelList.add(label.get());
                //turn label into something that we can use later to create label vector
            }
        }

        final LabelLookup labelLookup = LabelLookup.create(labelList);


        //a few params
        long max = 0;
        for (final List<S3DataPoint> oneDaysData : allData) {
            if (oneDaysData.isEmpty()) {
                continue;
            }

            Collections.sort(oneDaysData);

            final long duration = oneDaysData.get(oneDaysData.size()-1).time - oneDaysData.get(0).time;

            if (duration > max) {
                max = duration;
            }
        }

        final int numMinutes = (int) max / DateTimeConstants.MILLIS_PER_MINUTE;

        final List<DataSet> dsList = Lists.newArrayList();
        //now create datasets
        for (final List<S3DataPoint> oneDaysData : allData) {
            if (oneDaysData.isEmpty()) {
                continue;
            }

            final Optional<DataSet> ds = createDataSet(labelLookup,oneDaysData,numMinutes);


            if (!ds.isPresent()) {
                continue;
            }

            dsList.add(ds.get());


        }

        return new S3SleepDataSource(dsList);
    }

    private S3SleepDataSource(List<DataSet> dataSets) {
        this.dataSets = dataSets;
        numOutputs = NUM_LABELS;

        if (dataSets.isEmpty()) {
            numInputs = 0;
        }
        else {
            numInputs = dataSets.get(0).getFeatureMatrix().size(1);
        }

    }

    public List<DataSet> getDatasets() {
        return dataSets;
    }

    public int getNumInputs() {
        return numInputs;
    }

    public int getNumOutput() {
        return numOutputs;
    }

}
