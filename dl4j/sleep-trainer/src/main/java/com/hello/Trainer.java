package com.hello;

import com.google.common.base.Optional;
import org.deeplearning4j.nn.api.Layer;
import org.deeplearning4j.nn.api.OptimizationAlgorithm;
import org.deeplearning4j.nn.conf.MultiLayerConfiguration;
import org.deeplearning4j.nn.conf.NeuralNetConfiguration;
import org.deeplearning4j.nn.conf.Updater;
import org.deeplearning4j.nn.conf.distribution.UniformDistribution;
import org.deeplearning4j.nn.conf.layers.GravesLSTM;
import org.deeplearning4j.nn.conf.layers.RnnOutputLayer;
import org.deeplearning4j.nn.multilayer.MultiLayerNetwork;
import org.deeplearning4j.nn.weights.WeightInit;
import org.deeplearning4j.optimize.listeners.ScoreIterationListener;
import org.nd4j.linalg.api.ndarray.INDArray;
import org.nd4j.linalg.lossfunctions.LossFunctions;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.util.List;

/**
 * Created by benjo on 12/8/15.
 */
public class Trainer {

    final static Logger LOGGER = LoggerFactory.getLogger(Trainer.class);

    final static int LSTM_LAYER_SIZE = 10;

    public static void main(String [] args) throws Exception {

        final String path = "/Users/benjo/dev/Kasetsu/dl4j/sleep-trainer/data/";

        final Optional<SleepDataSource> dataOptional = SleepDataSource.createFromFile(path + "normiesAraw.json", path + "labels.csv");

        if (!dataOptional.isPresent()) {
            return;
        }

        final SleepDataSource data = dataOptional.get();

        MultiLayerConfiguration conf = new NeuralNetConfiguration.Builder()
                .optimizationAlgo(OptimizationAlgorithm.STOCHASTIC_GRADIENT_DESCENT)
                .iterations(1)
                .learningRate(0.1)
                .rmsDecay(0.95)
                .seed(12345)
                .regularization(true)
                .l2(0.001)
                .list(3)
                .layer(0, new GravesLSTM.Builder().nIn(data.inputColumns()).nOut(LSTM_LAYER_SIZE)
                        .updater(Updater.RMSPROP)
                        .activation("tanh").weightInit(WeightInit.DISTRIBUTION)
                        .dist(new UniformDistribution(-0.5, 0.5)).build())
                .layer(1, new GravesLSTM.Builder().nIn(LSTM_LAYER_SIZE).nOut(LSTM_LAYER_SIZE)
                        .updater(Updater.RMSPROP)
                        .activation("tanh").weightInit(WeightInit.DISTRIBUTION)
                        .dist(new UniformDistribution(-0.5, 0.5)).build())
                .layer(2, new RnnOutputLayer.Builder(LossFunctions.LossFunction.MCXENT).activation("softmax")        //MCXENT + softmax for classification
                        .updater(Updater.RMSPROP)
                        .nIn(LSTM_LAYER_SIZE).nOut(data.numOutcomes).weightInit(WeightInit.DISTRIBUTION)
                        .dist(new UniformDistribution(-0.08, 0.08)).build())
                .pretrain(false).backprop(true)
                .build();

        MultiLayerNetwork net = new MultiLayerNetwork(conf);

        net.init();

        net.printConfiguration();


        //net.setListeners(new ScoreIterationListener(1));


        //Print the  number of parameters in the network (and for each layer)
        Layer[] layers = net.getLayers();
        int totalNumParams = 0;
        for( int i=0; i<layers.length; i++ ){
            int nParams = layers[i].numParams();
            System.out.println("Number of parameters in layer " + i + ": " + nParams);
            totalNumParams += nParams;
        }
        System.out.println("Total number of network parameters: " + totalNumParams);


        for (int iEpoch = 0; iEpoch < 5; iEpoch++) {
            net.fit(data);

            System.out.println("Completed epoch " + iEpoch );

            data.reset();

        }

        final INDArray feats = data.next().getFeatureMatrix();

        final int [] result = net.predict(feats);



        int foo = 3;
        foo++;

    }

}
