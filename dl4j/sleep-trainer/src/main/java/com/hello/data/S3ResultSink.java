package com.hello.data;

import com.amazonaws.ClientConfiguration;
import com.amazonaws.auth.AWSCredentialsProvider;
import com.amazonaws.auth.DefaultAWSCredentialsProviderChain;
import com.amazonaws.services.s3.AmazonS3;
import com.amazonaws.services.s3.AmazonS3Client;
import org.apache.commons.io.FileUtils;
import org.deeplearning4j.nn.conf.MultiLayerConfiguration;
import org.deeplearning4j.nn.multilayer.MultiLayerNetwork;
import org.nd4j.linalg.factory.Nd4j;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.io.ByteArrayOutputStream;
import java.io.DataOutputStream;
import java.io.File;
import java.io.IOException;
import java.io.OutputStream;
import java.nio.file.Files;
import java.nio.file.Paths;

/**
 * Created by benjo on 2/12/16.
 */
public class S3ResultSink {
    final AmazonS3 amazonS3;
    final static String BUCKET = "hello-data/neuralnet";
    final static Logger LOGGER = LoggerFactory.getLogger(S3ResultSink.class);

    public S3ResultSink () {
        final AWSCredentialsProvider awsCredentialsProvider= new DefaultAWSCredentialsProviderChain();
        final ClientConfiguration clientConfiguration = new ClientConfiguration();

        amazonS3 = new AmazonS3Client(awsCredentialsProvider, clientConfiguration);

        final String foo = "hey there!";

    }

    public boolean saveNet(final MultiLayerNetwork net, MultiLayerConfiguration conf, final String key) {

        final ByteArrayOutputStream baos = new ByteArrayOutputStream();
        final DataOutputStream dos = new DataOutputStream(baos);

        try {
            Nd4j.write(net.params(), dos);
            S3Utils.putRegularS3Object(baos.toByteArray(),amazonS3,BUCKET,key + ".params");
            S3Utils.putRegularS3Object(conf.toJson().getBytes(),amazonS3,BUCKET,key + ".config");
        }
        catch (IOException e) {
            LOGGER.error(e.getMessage());
            return false;
        }

        return true;
    }
}
