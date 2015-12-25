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

    final static int NUM_ITER = 2;

    final static Logger LOGGER = LoggerFactory.getLogger(Trainer.class);

    final static int LSTM_LAYER_SIZE = 3;
    final static double UNIFORM_INIT_MAGNITUDE = 0.01;
    final static int MINI_BATCH_SIZE = 10;

    public static void main(String [] args) throws Exception {

        final String path = "/Users/benjo/dev/Kasetsu/dl4j/sleep-trainer/data/";

        final Optional<SleepDataSource> dataOptional = SleepDataSource.createFromFile(path + "normiesAraw.json", path + "labels.csv",MINI_BATCH_SIZE);

        if (!dataOptional.isPresent()) {
            return;
        }

        final SleepDataSource dataIterator = dataOptional.get();

        final Updater updater = Updater.RMSPROP;

        MultiLayerConfiguration conf = new NeuralNetConfiguration.Builder()
        //        .adamMeanDecay(0.9)
        //        .adamVarDecay(.999)
                .optimizationAlgo(OptimizationAlgorithm.STOCHASTIC_GRADIENT_DESCENT)
                .iterations(10)
                .learningRate(0.01)
                .rmsDecay(0.95)
                .seed(1)
                .regularization(true)
                .l2(0.001)
                .list(2)
                .layer(0, new GravesLSTM.Builder().nIn(dataIterator.inputColumns()).nOut(LSTM_LAYER_SIZE)
                        .updater(updater)
                        .activation("tanh").weightInit(WeightInit.DISTRIBUTION)
                        .dist(new UniformDistribution(-UNIFORM_INIT_MAGNITUDE, UNIFORM_INIT_MAGNITUDE)).build())
                .layer(1, new RnnOutputLayer.Builder(LossFunctions.LossFunction.MCXENT).activation("softmax")        //MCXENT + softmax for classification
                        .updater(updater)
                        .nIn(LSTM_LAYER_SIZE).nOut(dataIterator.numOutcomes).weightInit(WeightInit.DISTRIBUTION)
                        .dist(new UniformDistribution(-UNIFORM_INIT_MAGNITUDE, UNIFORM_INIT_MAGNITUDE)).build())
                .pretrain(false).backprop(true)
                .build();

        MultiLayerNetwork net = new MultiLayerNetwork(conf);

        net.init();
        net.printConfiguration();


        net.setListeners(new ScoreIterationListener(1));


        //Print the  number of parameters in the network (and for each layer)
        Layer[] layers = net.getLayers();
        int totalNumParams = 0;
        for( int i=0; i<layers.length; i++ ){
            int nParams = layers[i].numParams();
            System.out.println("Number of parameters in layer " + i + ": " + nParams);
            totalNumParams += nParams;
        }
        System.out.println("Total number of network parameters: " + totalNumParams);


        for (int iEpoch = 0; iEpoch < NUM_ITER; iEpoch++) {
            net.printConfiguration();

            net.fit(dataIterator);

            net.computeGradientAndScore();

            System.out.println("Completed epoch " + iEpoch );

            dataIterator.reset();


        }

        for (int idataset = 0; idataset < 1; idataset++) {
            final INDArray feats = dataIterator.next().getFeatureMatrix();

            final INDArray output = net.output(feats);

            int[] preds = new int[192];
            for (int i = 0; i < output.size(1); i++) {
                final INDArray row = output.slice(i);
                float themax = Float.NEGATIVE_INFINITY;
                int maxIdx = -1;
                final int len = row.size(0);
                for (int j = 0; j < len; j++) {
                    if (row.getFloat(j) > themax) {
                        themax = row.getFloat(j);
                        maxIdx = j;
                    }

                    preds[i] = maxIdx;
                }

                LOGGER.info("{}",preds);


            }

            int foo = 3;
            foo++;
        }




    }

}
