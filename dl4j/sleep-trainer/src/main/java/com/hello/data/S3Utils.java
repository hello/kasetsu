package com.hello.data;

import com.amazonaws.services.s3.AmazonS3;
import com.amazonaws.services.s3.model.GetObjectRequest;
import com.amazonaws.services.s3.model.S3Object;
import com.google.common.io.CharStreams;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.io.IOException;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.util.zip.GZIPInputStream;

/**
 * Created by benjo on 2/11/16.
 */
public class S3Utils {
    final static Logger LOGGER = LoggerFactory.getLogger(S3Utils.class);

    public static String getZippedS3Object(final AmazonS3 s3, final String bucket, final String key) {

        final S3Object s3Object = s3.getObject(new GetObjectRequest(bucket, key));
        try (final InputStream stream = new GZIPInputStream(s3Object.getObjectContent())) {
            final InputStreamReader inputStreamReader = new InputStreamReader(stream);
            return CharStreams.toString(inputStreamReader);
        }
        catch (IOException e) {
            LOGGER.error(e.getMessage());
        }

        return "";
    }

    public static String getRegularS3Object(final AmazonS3 s3, final String bucket, final String key) {
        final S3Object s3Object = s3.getObject(new GetObjectRequest(bucket, key));

        try (final InputStream stream = s3Object.getObjectContent()) {
            final InputStreamReader inputStreamReader = new InputStreamReader(stream);
            return CharStreams.toString(inputStreamReader);

        }
        catch (IOException e) {
            LOGGER.error(e.getMessage());
        }
        return "";

    }
}
