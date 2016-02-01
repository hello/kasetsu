package com.hello;

import com.google.common.base.Optional;
import org.apache.commons.io.FileUtils;
import org.deeplearning4j.eval.Evaluation;
import org.deeplearning4j.nn.api.Layer;
import org.deeplearning4j.nn.api.OptimizationAlgorithm;
import org.deeplearning4j.nn.conf.MultiLayerConfiguration;
import org.deeplearning4j.nn.conf.NeuralNetConfiguration;
import org.deeplearning4j.nn.conf.Updater;
import org.deeplearning4j.nn.conf.distribution.UniformDistribution;
//import org.deeplearning4j.nn.conf.layers.GravesBidirectionalLSTM;
import org.deeplearning4j.nn.conf.layers.GravesLSTM;
import org.deeplearning4j.nn.conf.layers.RnnOutputLayer;
import org.deeplearning4j.nn.multilayer.MultiLayerNetwork;
import org.deeplearning4j.nn.weights.WeightInit;
import org.deeplearning4j.optimize.listeners.ScoreIterationListener;
import org.nd4j.linalg.api.ndarray.INDArray;
import org.nd4j.linalg.dataset.DataSet;
import org.nd4j.linalg.factory.Nd4j;
import org.nd4j.linalg.lossfunctions.LossFunctions;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.io.DataOutputStream;
import java.io.File;
import java.io.IOException;
import java.io.OutputStream;
import java.nio.file.Files;
import java.nio.file.Paths;

/**
 * Created by benjo on 12/8/15.
 */
public class Trainer {

    final static String NET_FILE_NAME = "data/net7.bin";


    final static int NUM_EPOCHS = 500;
    final static int NUM_ITERS = 1;
    final static double LEARNING_RATE = 0.003;
    final static Updater UPDATER = Updater.RMSPROP;

    final static Logger LOGGER = LoggerFactory.getLogger(Trainer.class);

    final static int LSTM_LAYER_SIZE = 2;
    final static double UNIFORM_INIT_MAGNITUDE = 0.01;
    final static int MINI_BATCH_SIZE = 3;

    public static void saveNet(final MultiLayerNetwork net,MultiLayerConfiguration conf,final String filename) {

        final ClassLoader cl = Trainer.class.getClassLoader();
        final String baseDir = cl.getResource("").getFile();
        final String fileFullPath = baseDir + filename;
        final String confFileFullPath = baseDir + filename + ".conf";

        final File file = new File(fileFullPath);
        final File confFile = new File(confFileFullPath);

        try {
            final OutputStream fos = Files.newOutputStream(Paths.get(file.getAbsolutePath()));
            final DataOutputStream dos = new DataOutputStream(fos);

            Nd4j.write(net.params(), dos);

            dos.flush();
            dos.close();

            FileUtils.writeStringToFile(confFile, conf.toJson());


        } catch (IOException e) {
            e.printStackTrace();
        }


    }

    public static void main(String [] args) throws Exception {

        final String rawDataFilePath = args[0];
        final String labelsFilePath = args[1];


        final Optional<SleepDataSource> dataOptional = SleepDataSource.createFromFile(rawDataFilePath,labelsFilePath,MINI_BATCH_SIZE);

        if (!dataOptional.isPresent()) {
            return;
        }

        final SleepDataSource dataIterator = dataOptional.get();


        final MultiLayerConfiguration conf = new NeuralNetConfiguration.Builder()
                .optimizationAlgo(OptimizationAlgorithm.STOCHASTIC_GRADIENT_DESCENT)
                .iterations(NUM_ITERS)
                .learningRate(LEARNING_RATE)
                .rmsDecay(0.95)
                .seed(1)
                .regularization(true)
                .l2(0.001)
                .list(3)
                .layer(0, new GravesLSTM.Builder().nIn(dataIterator.inputColumns()).nOut(LSTM_LAYER_SIZE)
                        .updater(UPDATER)
                        .dropOut(0.5)
                        .activation("tanh").weightInit(WeightInit.DISTRIBUTION)
                        .dist(new UniformDistribution(-UNIFORM_INIT_MAGNITUDE, UNIFORM_INIT_MAGNITUDE)).build())

                .layer(1, new GravesLSTM.Builder().nIn(LSTM_LAYER_SIZE).nOut(LSTM_LAYER_SIZE)
                        .updater(UPDATER)
                        .dropOut(0.5)
                        .activation("tanh").weightInit(WeightInit.DISTRIBUTION)
                        .dist(new UniformDistribution(-UNIFORM_INIT_MAGNITUDE, UNIFORM_INIT_MAGNITUDE)).build())

                .layer(2, new RnnOutputLayer.Builder(LossFunctions.LossFunction.MCXENT).activation("softmax")        //MCXENT + softmax for classification
                        .updater(UPDATER)
                        .nIn(LSTM_LAYER_SIZE).nOut(dataIterator.numOutcomes).weightInit(WeightInit.DISTRIBUTION)
                        .dist(new UniformDistribution(-UNIFORM_INIT_MAGNITUDE, UNIFORM_INIT_MAGNITUDE)).build())
                .pretrain(false).backprop(true)
                .build();

        final MultiLayerNetwork net = new MultiLayerNetwork(conf);

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

        for (int iEpoch = 0; iEpoch < NUM_EPOCHS; iEpoch++) {
            net.fit(dataIterator);

            dataIterator.reset();

            final Evaluation eval = new Evaluation();
            final DataSet ds = DataSet.merge(dataIterator.dataSets);

            final INDArray output = net.output(ds.getFeatureMatrix());
            eval.evalTimeSeries(ds.getLabels(), output);
            LOGGER.info(eval.stats());

            saveNet(net,conf,NET_FILE_NAME);

            System.out.println("Completed epoch " + iEpoch );

            dataIterator.reset();


        }

        final Evaluation eval = new Evaluation();
        final DataSet ds = DataSet.merge(dataIterator.dataSets);

        final INDArray output = net.output(ds.getFeatureMatrix());

        int foo = 3;
        foo++;





    }

}
