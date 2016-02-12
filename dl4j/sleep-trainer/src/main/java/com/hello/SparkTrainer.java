package com.hello;


import java.util.List;

import com.clearspring.analytics.util.Lists;
import com.google.common.base.Optional;
import com.hello.data.S3SleepDataSource;
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
import org.deeplearning4j.nn.conf.layers.GravesLSTM;
import org.deeplearning4j.nn.conf.layers.RnnOutputLayer;
import org.deeplearning4j.nn.multilayer.MultiLayerNetwork;
import org.deeplearning4j.nn.weights.WeightInit;
import org.deeplearning4j.spark.impl.multilayer.SparkDl4jMultiLayer;
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
    final static int NUM_EPOCHS = 500;
    final static int NUM_ITERS = 10;
    final static double LEARNING_RATE = 0.003;
    final static Updater UPDATER = Updater.RMSPROP;

    final static Logger LOGGER = LoggerFactory.getLogger(SparkTrainer.class);

    final static int LSTM_LAYER_SIZE = 2;
    final static double UNIFORM_INIT_MAGNITUDE = 0.01;
    final static int MINI_BATCH_SIZE = 3;
    final static int NUM_CORES = 4;

    public static void main(String[] args) throws Exception {
//Number of CPU cores to use for training
        final ch.qos.logback.classic.Logger root = (ch.qos.logback.classic.Logger)LoggerFactory.getLogger(Logger.ROOT_LOGGER_NAME);
        root.setLevel(Level.ERROR);

        final S3SleepDataSource sleepDataSource =
                S3SleepDataSource.create(
                        "hello-data/neuralnet",
                        new String[]{"Jan15.csv000.gz"},
                        new String[]{"labels_sleep_2016-01-01_2016-02-05.csv000.gz"});



        final String rawDataFilePath = args[0];
        final String labelsFilePath = args[1];


        final Optional<SleepDataSource> dataOptional = SleepDataSource.createFromFile(rawDataFilePath,labelsFilePath,MINI_BATCH_SIZE);

        if (!dataOptional.isPresent()) {
            return;
        }

        final SleepDataSource dataIterator = dataOptional.get();

        final List<DataSet> dataSetList = Lists.newArrayList();
        while (dataIterator.hasNext()) {
            dataSetList.add(dataIterator.next());
        }


        SparkConf sparkConf = new SparkConf();
        sparkConf.setMaster("local[" + NUM_CORES + "]");
        sparkConf.setAppName("LSTM_Char");
        sparkConf.set(SparkDl4jMultiLayer.AVERAGE_EACH_ITERATION, String.valueOf(true));

        final JavaSparkContext sc = new JavaSparkContext(sparkConf);

        final JavaRDD<DataSet> dsParallel = sc.parallelize(dataSetList);
        dsParallel.persist(StorageLevel.MEMORY_ONLY());


        //------------------------------//
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




        MultiLayerNetwork net = new MultiLayerNetwork(conf);

        net.init();
        net.setUpdater(null);   //Workaround for a minor bug in 0.4-rc3.8
        net.printConfiguration();

        final SparkDl4jMultiLayer sparkNetwork = new SparkDl4jMultiLayer(sc, net);


        for (int i = 0; i < NUM_EPOCHS; i++) {
            sparkNetwork.fitDataSet(dsParallel);


            final DataSet ds = DataSet.merge(dataSetList);

            net = sparkNetwork.fitDataSet(dsParallel);

            {
                final Evaluation eval = new Evaluation();
                final DataSet ds2 = DataSet.merge(dataIterator.dataSets);

                final INDArray output = net.output(ds2.getFeatureMatrix());
                eval.evalTimeSeries(ds2.getLabels(), output);
                LOGGER.error(eval.stats());
            }
        }


    }
}