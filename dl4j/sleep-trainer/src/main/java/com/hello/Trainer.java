package com.hello;

import com.google.common.base.Optional;
import com.hello.data.S3SleepDataSource;
import org.apache.commons.io.FileUtils;
import org.deeplearning4j.eval.Evaluation;
import org.deeplearning4j.nn.api.Layer;
import org.deeplearning4j.nn.api.OptimizationAlgorithm;
import org.deeplearning4j.nn.conf.MultiLayerConfiguration;
import org.deeplearning4j.nn.conf.NeuralNetConfiguration;
import org.deeplearning4j.nn.conf.Updater;
import org.deeplearning4j.nn.conf.distribution.UniformDistribution;
//import org.deeplearning4j.nn.conf.layers.GravesBidirectionalLSTM;
import org.deeplearning4j.nn.conf.layers.GravesBidirectionalLSTM;
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
import java.util.List;
import org.slf4j.LoggerFactory;
import ch.qos.logback.classic.Level;
/**
 * Created by benjo on 12/8/15.
 */
public class Trainer {

    final static String NET_BUCKET = "hello-data/neuralnet";
    final static String NET_BASE_KEY = "2016-02-21T21:55:39.746Z";

    final static String DATA_BUCKET = "hello-data/neuralnet";
    final static String [] DATA_FILES = new String[]{
            "2016-01-02.csv000.gz"};
    final static String [] LABEL_FILES = new String[]{"labels_sleep_2016-01-01_2016-02-05.csv000.gz"};

    final static int NUM_EPOCHS = 500;
    final static int NUM_ITERS = 1;
    final static double LEARNING_RATE = 0.15;
    final static Updater UPDATER = Updater.RMSPROP;

    final static Logger LOGGER = LoggerFactory.getLogger(Trainer.class);

    final static int LSTM_LAYER_SIZE = 7;
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


        ch.qos.logback.classic.Logger root = (ch.qos.logback.classic.Logger)LoggerFactory.getLogger(Logger.ROOT_LOGGER_NAME);
        root.setLevel(Level.INFO);

        final S3SleepDataSource dataIterator =
                S3SleepDataSource.create(
                        "hello-data/neuralnet",
                        new String[]{
                                "2016-01-01.csv000.gz",
                                "2016-01-02.csv000.gz",
                                "2016-01-03.csv000.gz",
                                "2016-01-04.csv000.gz",
                                "2016-01-05.csv000.gz",
                                "2016-01-06.csv000.gz",
                                "2016-01-07.csv000.gz",
                                "2016-01-08.csv000.gz",
                                "2016-01-09.csv000.gz",
                                "2016-01-10.csv000.gz",
                                "2016-01-11.csv000.gz",
                                "2016-01-12.csv000.gz",
                                "2016-01-13.csv000.gz",
                                "2016-01-14.csv000.gz",
                                "2016-01-15.csv000.gz",
                                "2016-01-16.csv000.gz",
                                "2016-01-17.csv000.gz",
                                "2016-01-18.csv000.gz",
                                "2016-01-19.csv000.gz",
                                "2016-01-20.csv000.gz",
                                "2016-01-21.csv000.gz",
                                "2016-01-22.csv000.gz",
                                "2016-01-23.csv000.gz",
                                "2016-01-24.csv000.gz",
                                "2016-01-25.csv000.gz",
                                "2016-01-26.csv000.gz",
                                "2016-01-27.csv000.gz",
                                "2016-01-28.csv000.gz",
                                "2016-01-29.csv000.gz",
                                "2016-01-30.csv000.gz",
                                "2016-01-31.csv000.gz",
                                "2016-02-01.csv000.gz",
                                "2016-02-02.csv000.gz",
                                "2016-02-03.csv000.gz"},
                        new String[]{"labels_sleep_2016-01-01_2016-02-05.csv000.gz"});


        dataIterator.setBatchFraction(0.05);

        final MultiLayerConfiguration conf = new NeuralNetConfiguration.Builder()
                .optimizationAlgo(OptimizationAlgorithm.STOCHASTIC_GRADIENT_DESCENT)
                .iterations(NUM_ITERS)
                .learningRate(LEARNING_RATE)
                .rmsDecay(0.95)
                .seed(1)
                .regularization(true)
                .l2(0.001)
                .list(3)
                .layer(0,new GravesBidirectionalLSTM.Builder().nIn(dataIterator.inputColumns()).nOut(LSTM_LAYER_SIZE)
                        .updater(UPDATER)
                        .dropOut(0.5)
                        .activation("tanh").weightInit(WeightInit.DISTRIBUTION)
                        .dist(new UniformDistribution(-UNIFORM_INIT_MAGNITUDE, UNIFORM_INIT_MAGNITUDE)).build())

                .layer(1, new GravesBidirectionalLSTM.Builder().nIn(LSTM_LAYER_SIZE).nOut(LSTM_LAYER_SIZE)
                        .updater(UPDATER)
                        .dropOut(0.5)
                        .activation("tanh").weightInit(WeightInit.DISTRIBUTION)
                        .dist(new UniformDistribution(-UNIFORM_INIT_MAGNITUDE, UNIFORM_INIT_MAGNITUDE)).build())

                .layer(2, new RnnOutputLayer.Builder(LossFunctions.LossFunction.MCXENT).activation("softmax")        //MCXENT + softmax for classification
                        .updater(UPDATER)
                        .nIn(LSTM_LAYER_SIZE).nOut(dataIterator.getNumOutput()).weightInit(WeightInit.DISTRIBUTION)
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
            final DataSet ds = DataSet.merge(dataIterator.getDatasets());

            final INDArray output = net.output(ds.getFeatureMatrix());
            eval.evalTimeSeries(ds.getLabels(), output);
            LOGGER.info(eval.stats());

            saveNet(net,conf,"foobars.bars.foo.bars");

            System.out.println("Completed epoch " + iEpoch );

            dataIterator.reset();


        }

        final Evaluation eval = new Evaluation();
        final DataSet ds = DataSet.merge(dataIterator.getDatasets());

        final INDArray output = net.output(ds.getFeatureMatrix());

        int foo = 3;
        foo++;





    }

}
