package com.hello.alg.runners;

import com.google.common.base.Optional;
import com.hello.alg.helpers.NeuralNetClient;
import com.hello.alg.helpers.TimelineProcessorWrapper;
import com.hello.alg.model.TimelineProcessorOutput;
import com.hello.suripu.core.algorithmintegration.AlgorithmConfiguration;
import org.apache.http.impl.client.HttpClientBuilder;


import java.io.BufferedReader;
import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Paths;

/**
 * Created by benjo on 12/9/16.
 */
public class TimelineNeuralNetRunner {


    final static String NEURAL_NET_ENDPOINT = "/net";


    public static void main(String [] args ) throws IOException {

        final String neuralNetUrl = args[0];
        final String filename = args[1];

        //our keras server somewhere
        //TODO configure this client to point at the right server
        final NeuralNetClient neuralNetEndpoint = NeuralNetClient.create(
                HttpClientBuilder.create().build(),
                neuralNetUrl + NEURAL_NET_ENDPOINT);


        final TimelineProcessorWrapper timelineProcessorWrapper = new TimelineProcessorWrapper(neuralNetEndpoint);

        try(BufferedReader reader = Files.newBufferedReader(Paths.get(filename), StandardCharsets.UTF_8)) {
            String line;
            while ((line = reader.readLine()) != null) {
                // each line should be base64 binary data that is a protobuf

                final Optional<TimelineProcessorOutput> result = timelineProcessorWrapper.setDataAndRun(line);

                if (!result.isPresent()) {
                    continue;
                }

                //TODO convert result to JSON
                System.out.print(result.get());

            }
        }





    }


}
