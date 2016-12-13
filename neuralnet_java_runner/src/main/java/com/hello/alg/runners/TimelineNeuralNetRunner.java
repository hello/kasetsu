package com.hello.alg.runners;

import com.hello.alg.helpers.NeuralNetClient;
import com.hello.suripu.core.algorithmintegration.AlgorithmConfiguration;
import com.hello.suripu.core.algorithmintegration.NeuralNetAlgorithm;
import com.hello.suripu.core.algorithmintegration.OneDaysSensorData;
import org.apache.http.impl.client.HttpClientBuilder;


import java.io.IOException;

/**
 * Created by benjo on 12/9/16.
 */
public class TimelineNeuralNetRunner {


    final static String NEURAL_NET_ENDPOINT = "/net";

    final static AlgorithmConfiguration algorithmConfiguration = new AlgorithmConfiguration() {
        @Override
        public int getArtificalLightStartMinuteOfDay() {
            return 0;
        }

        @Override
        public int getArtificalLightStopMinuteOfDay() {
            return 0;
        }
    };

    public static void main(String [] args ) throws IOException {

        final NeuralNetClient client = NeuralNetClient.create(
                HttpClientBuilder.create().build(),
                NEURAL_NET_ENDPOINT);

        final NeuralNetAlgorithm neuralNetAlgorithm = new NeuralNetAlgorithm(client,algorithmConfiguration);

        final OneDaysSensorData oneDaysSensorData = new OneDaysSensorData();

        neuralNetAlgorithm.getTimelinePrediction()

    }


}
