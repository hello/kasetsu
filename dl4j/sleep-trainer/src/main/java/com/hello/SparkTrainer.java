package com.hello;


import java.util.List;

import com.amazonaws.ClientConfiguration;
import com.amazonaws.auth.AWSCredentialsProvider;
import com.amazonaws.auth.DefaultAWSCredentialsProviderChain;
import com.amazonaws.services.s3.AmazonS3;
import com.amazonaws.services.s3.AmazonS3Client;
import com.google.common.base.Optional;
import com.hello.data.NeuralNetAndInfo;
import com.hello.data.S3NeuralNet;
import com.hello.data.S3ResultSink;
import com.hello.data.S3SleepDataSource;
import com.hello.data.S3Utils;
import org.apache.spark.SparkConf;
import org.apache.spark.api.java.JavaRDD;
import org.apache.spark.api.java.JavaSparkContext;
import org.apache.spark.storage.StorageLevel;
import org.deeplearning4j.eval.Evaluation;
import org.deeplearning4j.nn.api.OptimizationAlgorithm;
import org.deeplearning4j.nn.conf.MultiLayerConfiguration;
import org.deeplearning4j.nn.conf.NeuralNetConfiguration;
import org.deeplearning4j.nn.conf.Updater;
import org.deeplearning4j.nn.conf.distribution.UniformDistribution;
import org.deeplearning4j.nn.conf.layers.GravesBidirectionalLSTM;
import org.deeplearning4j.nn.conf.layers.GravesLSTM;
import org.deeplearning4j.nn.conf.layers.RnnOutputLayer;
import org.deeplearning4j.nn.multilayer.MultiLayerNetwork;
import org.deeplearning4j.nn.weights.WeightInit;
import org.deeplearning4j.optimize.listeners.ScoreIterationListener;
import org.deeplearning4j.spark.impl.multilayer.SparkDl4jMultiLayer;
import org.joda.time.DateTime;
import org.nd4j.linalg.api.ndarray.INDArray;
import org.nd4j.linalg.dataset.DataSet;
import org.nd4j.linalg.lossfunctions.LossFunctions;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import ch.qos.logback.classic.Level;


/**
 * Created by benjo on 1/24/16.
 */
public class SparkTrainer {
    final static int NUM_EPOCHS = 1000;
    final static int NUM_ITERS = 3;
    final static double LEARNING_RATE = 0.15;
    final static Updater UPDATER = Updater.RMSPROP;

    final static Logger LOGGER = LoggerFactory.getLogger(SparkTrainer.class);

    final static int LSTM_LAYER_SIZE = 7;
    final static double UNIFORM_INIT_MAGNITUDE = 0.01;
    final static int NUM_CORES = 8;

    final static String NET_BUCKET = "hello-data/neuralnet";
    final static String NET_BASE_KEY = "2016-02-21T21:55:39.746Z";
    final static boolean LOAD_FROM_S3 = true;

    public static void main(String[] args) throws Exception {
//Number of CPU cores to use for training
        LoggerUtils.setDefaultLoggingLevel(Level.INFO);

        final S3ResultSink resultSink = new S3ResultSink();

        final S3SleepDataSource sleepDataSource =
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






        final List<DataSet> dataSetList = sleepDataSource.getDatasets();

        System.out.format("found %d user days of data\n",dataSetList.size());

        SparkConf sparkConf = new SparkConf();
        sparkConf.setMaster("local[" + NUM_CORES + "]");
        sparkConf.setAppName("LSTM_sleep");
        sparkConf.set(SparkDl4jMultiLayer.AVERAGE_EACH_ITERATION, String.valueOf(true));

        final JavaSparkContext sc = new JavaSparkContext(sparkConf);

        final JavaRDD<DataSet> dsParallel = sc.parallelize(dataSetList);
        dsParallel.persist(StorageLevel.MEMORY_ONLY());


        //------------------------------//
        MultiLayerNetwork net = null;
        MultiLayerConfiguration conf = null;

        if (!LOAD_FROM_S3) {
            conf = new NeuralNetConfiguration.Builder()
                    .optimizationAlgo(OptimizationAlgorithm.STOCHASTIC_GRADIENT_DESCENT)
                    .iterations(NUM_ITERS)
                    .learningRate(LEARNING_RATE)
                    .rmsDecay(0.95)
                    .seed(1)
                    .regularization(true)
                    .l2(0.001)
                    .list(3)
                    .layer(0, new GravesBidirectionalLSTM.Builder().nIn(sleepDataSource.getNumInputs()).nOut(LSTM_LAYER_SIZE)
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
                            .nIn(LSTM_LAYER_SIZE).nOut(sleepDataSource.getNumOutput()).weightInit(WeightInit.DISTRIBUTION)
                            .dist(new UniformDistribution(-UNIFORM_INIT_MAGNITUDE, UNIFORM_INIT_MAGNITUDE)).build())
                    .pretrain(false).backprop(true)
                    .build();


            net = new MultiLayerNetwork(conf);
        }
        else {
            final Optional<NeuralNetAndInfo> netAndInfo = S3NeuralNet.getNet(NET_BUCKET, NET_BASE_KEY);

            if (netAndInfo.isPresent()) {
                LOGGER.info("successfully pulled net from S3");
                net = netAndInfo.get().net;
                conf = netAndInfo.get().conf;
            }
        }

        if (net == null) {
            LOGGER.error("NO VALID NEURAL NET FOUND");
            return;
        }
        net.init();
        net.setUpdater(null);   //Workaround for a minor bug in 0.4-rc3.8
        net.printConfiguration();
        net.setListeners(new ScoreIterationListener(1));

        final SparkDl4jMultiLayer sparkNetwork = new SparkDl4jMultiLayer(sc, net);


        for (int i = 0; i < NUM_EPOCHS; i++) {
            sparkNetwork.fitDataSet(dsParallel);


            final DataSet ds = DataSet.merge(dataSetList);

            net = sparkNetwork.fitDataSet(dsParallel);

            {
                final Evaluation eval = new Evaluation();
                final DataSet ds2 = DataSet.merge(sleepDataSource.getDatasets());
                final INDArray output = net.output(ds2.getFeatureMatrix());
                eval.evalTimeSeries(ds2.getLabels(), output);
                LOGGER.info(eval.stats());

                if (i % 20 == 0) {
                    resultSink.saveNet(net, conf, DateTime.now().toString());
                }
            }
        }

        resultSink.saveNet(net,conf, DateTime.now().toString());

    }
}
