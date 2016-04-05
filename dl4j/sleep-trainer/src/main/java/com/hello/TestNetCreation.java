package com.hello;

import org.deeplearning4j.nn.api.OptimizationAlgorithm;
import org.deeplearning4j.nn.conf.MultiLayerConfiguration;
import org.deeplearning4j.nn.conf.NeuralNetConfiguration;
import org.deeplearning4j.nn.conf.Updater;
import org.deeplearning4j.nn.conf.distribution.UniformDistribution;
import org.deeplearning4j.nn.conf.layers.GravesBidirectionalLSTM;
import org.deeplearning4j.nn.conf.layers.RnnOutputLayer;
import org.deeplearning4j.nn.multilayer.MultiLayerNetwork;
import org.deeplearning4j.nn.weights.WeightInit;
import org.nd4j.linalg.lossfunctions.LossFunctions;

public class TestNetCreation {
    final static int NUM_ITERS = 1;
    final static float LEARNING_RATE = 0.15f;
    final static Updater UPDATER = Updater.RMSPROP;


    final static int LSTM_LAYER_SIZE = 7;
    final static float UNIFORM_INIT_MAGNITUDE = 0.01f;

    final static int INPUT_COLUMS = 7;

    public static void main(String [] args) {
        final MultiLayerConfiguration conf = new NeuralNetConfiguration.Builder()
                .optimizationAlgo(OptimizationAlgorithm.STOCHASTIC_GRADIENT_DESCENT)
                .iterations(NUM_ITERS)
                .learningRate(LEARNING_RATE)
                .rmsDecay(0.95f)
                .seed(1)
                .regularization(true)
                .l2(0.001f)
                .list()
                .layer(0,new GravesBidirectionalLSTM.Builder().nIn(INPUT_COLUMS).nOut(LSTM_LAYER_SIZE)
                        .updater(UPDATER)
                        .dropOut(0.5f)
                        .activation("tanh").weightInit(WeightInit.DISTRIBUTION)
                        .dist(new UniformDistribution(-UNIFORM_INIT_MAGNITUDE, UNIFORM_INIT_MAGNITUDE)).build())

                .layer(1, new GravesBidirectionalLSTM.Builder().nIn(LSTM_LAYER_SIZE).nOut(LSTM_LAYER_SIZE)
                        .updater(UPDATER)
                        .dropOut(0.5f)
                        .activation("tanh").weightInit(WeightInit.DISTRIBUTION)
                        .dist(new UniformDistribution(-UNIFORM_INIT_MAGNITUDE, UNIFORM_INIT_MAGNITUDE)).build())

                .layer(2, new RnnOutputLayer.Builder(LossFunctions.LossFunction.MCXENT).activation("softmax")        //MCXENT + softmax for classification
                        .updater(UPDATER)
                        .nIn(LSTM_LAYER_SIZE).nOut(INPUT_COLUMS).weightInit(WeightInit.DISTRIBUTION)
                        .dist(new UniformDistribution(-UNIFORM_INIT_MAGNITUDE, UNIFORM_INIT_MAGNITUDE)).build())
                .pretrain(false).backprop(true)
                .build();

        final MultiLayerNetwork net = new MultiLayerNetwork(conf);

        net.init();
    }
}
