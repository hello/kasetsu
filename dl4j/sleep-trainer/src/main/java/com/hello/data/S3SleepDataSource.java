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
import org.nd4j.linalg.dataset.DataSet;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.io.IOException;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.util.List;
import java.util.Scanner;
import java.util.zip.GZIPInputStream;

/**
 * Created by benjo on 2/10/16.
 */
public class S3SleepDataSource {
    final static Logger LOGGER = LoggerFactory.getLogger(S3SleepDataSource.class);


    public static S3SleepDataSource create(final String bucket, final String [] datakeys, final String[] labelkeys) {
        final List<List<S3DataPoint>> allData = Lists.newArrayList();

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

        final LabelLookup labels = LabelLookup.create(labelList);


        //now create datasets

        for (final List<S3DataPoint> oneDaysData : allData) {
            if (oneDaysData.isEmpty()) {
                continue;
            }

            final long accountId = oneDaysData.get(0).accountId;

            labels.getLabel(accountId,oneDaysData.get(0).time);


        }

        return new S3SleepDataSource();
    }



    //TODO go from current data to dataset
    public List<DataSet> getDataset() {
        return Lists.newArrayList();
    }

}
