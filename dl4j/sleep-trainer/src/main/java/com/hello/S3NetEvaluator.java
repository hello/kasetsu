package com.hello;

import com.google.common.base.Optional;
import com.hello.data.S3NeuralNet;
import com.hello.data.S3SleepDataSource;
import com.xeiam.xchart.Chart;
import com.xeiam.xchart.QuickChart;
import com.xeiam.xchart.SwingWrapper;
import org.deeplearning4j.nn.multilayer.MultiLayerNetwork;
import org.nd4j.linalg.api.ndarray.INDArray;
import org.nd4j.linalg.dataset.DataSet;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.util.List;

/**
 * Created by benjo on 2/17/16.
 */
public class S3NetEvaluator {
    final static Logger LOGGER = LoggerFactory.getLogger(S3NetEvaluator.class);

    final static String BUCKET = "hello-data/neuralnet";
    final static String NET_BASE_KEY = "2016-02-18T19:27:27.776Z";
    final static String [] DATA_FILES = new String[]{
            "2016-01-01.csv000.gz"};
    final static String [] LABEL_FILES = new String[]{"labels_sleep_2016-01-01_2016-02-05.csv000.gz"};

    public static void main(final String [] args) {

        final Optional<MultiLayerNetwork> net = S3NeuralNet.getNet(BUCKET, NET_BASE_KEY);

        if (!net.isPresent()) {
            LOGGER.error("could not find valid neural net in {}/{}",BUCKET, NET_BASE_KEY);
            return;
        }

        final S3SleepDataSource sleepDataSource =
                S3SleepDataSource.create(
                        BUCKET,
                        DATA_FILES,
                        LABEL_FILES);




        final List<DataSet> dss = sleepDataSource.getDatasets();
        int count = 0;
        for (DataSet ds : dss) {

            final INDArray output = net.get().output(ds.getFeatureMatrix()).slice(0);

            final INDArray mat = ds.getFeatureMatrix().slice(0);
            final int T = mat.columns();
            final int N = mat.rows();

            final double [][] arr = new double[N + 1][T];

            for (int t= 0 ; t < T; t++) {
                arr[0][t] = output.getRow(1).getDouble(t) * 10.0;
            }

            for (int i = 0; i < N; i++) {
                for (int t= 0 ; t < T; t++) {
                    arr[i + 1][t] = mat.getRow(i).getDouble(t);
                }
            }

            final int len = arr[0].length;

            final double [] x = new double[T];
            for (int t = 0; t < T; t++) {
                x[t] = t;
            }

            final String [] series = new String[N + 1];
            for (int i = 0; i < N + 1; i++) {
                series[i] = String.valueOf(i);
            }
                // Create Chart
            final Chart chart = QuickChart.getChart("data","index","",series,x,arr);
            final SwingWrapper sw = new SwingWrapper(chart);
            sw.displayChart(String.valueOf(count++));

            int foo = 0;

            foo++;

        }


    }

}
