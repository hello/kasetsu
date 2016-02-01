package com.hello;

import com.google.common.base.Optional;
import org.apache.commons.io.FileUtils;
import org.deeplearning4j.eval.Evaluation;
import org.deeplearning4j.nn.conf.MultiLayerConfiguration;
import org.deeplearning4j.nn.conf.NeuralNetConfiguration;
import org.deeplearning4j.nn.multilayer.MultiLayerNetwork;
import org.nd4j.linalg.api.ndarray.INDArray;
import org.nd4j.linalg.dataset.DataSet;
import org.nd4j.linalg.factory.Nd4j;
import org.nd4j.linalg.indexing.INDArrayIndex;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.io.*;
import java.nio.file.Files;
import java.nio.file.Paths;

/**
 * Created by benjo on 12/26/15.
 */
public class NetEvaluator {

    final static Logger LOGGER = LoggerFactory.getLogger(NetEvaluator.class);


    public static void main(String [] args) throws Exception {

        if (args.length < 2) {
            LOGGER.info("need args as neural.net, then the features.json filename");
            return;
        }

        final String netFilename = args[0];
        final String dataFilename = args[1];

        String labelsPath = "";

        if (args.length == 3) {
            labelsPath = args[2];
        }

        final Optional<SleepDataSource> dataOptional = SleepDataSource.createFromFile(dataFilename,labelsPath,0);

        if (!dataOptional.isPresent()) {
            LOGGER.error("failed to load data sources");
            return;
        }

        final SleepDataSource data = dataOptional.get();

        final Optional<MultiLayerNetwork> networkOptional = loadNet(netFilename);

        if (!networkOptional.isPresent()) {
            LOGGER.error("failed to load network {}",netFilename);
            return;
        }

        final MultiLayerNetwork net = networkOptional.get();

        int count = 0;
        //if labels were included
        if (!data.dataSets.isEmpty() && true) {
            final Evaluation eval = new Evaluation();
            final DataSet ds = DataSet.merge(data.dataSets);

            final INDArray output = net.output(ds.getFeatureMatrix());
            eval.evalTimeSeries(ds.getLabels(), output);
            LOGGER.info(eval.stats());

        }
        else {
            //no labels specified
            for (final INDArray feats : data.unusedFeatures) {
                final INDArray featArray = feats.slice(0);
                final INDArray output = net.output(feats);
                final INDArray x1 = featArray.slice(0);
                final INDArray x2 = featArray.slice(1);
                final INDArray x4 = featArray.slice(4);
                final INDArray x5 = featArray.slice(5);

                final INDArray sleep = output.slice(0).getRow(1).transpose();

                LOGGER.info("---{}---",count++);
                LOGGER.info("\n\ny = {};\n x1={};\n x2 = {} \n x4={}\n x5={}\n",sleep,x1,x2,x4,x5);





            }
        }

    }

    private static Optional<MultiLayerNetwork> loadNet(final String filename) {

        try {

            final ClassLoader cl = NetEvaluator.class.getClassLoader();
            final File file = new File(cl.getResource(filename).getFile());
            final File confFile = new File(cl.getResource(filename + ".conf").getFile());

            final InputStream ios = Files.newInputStream(Paths.get(file.getAbsolutePath()));
            final DataInputStream dis = new DataInputStream(ios);

            final INDArray params = Nd4j.read(dis);

            dis.close();

            final String json = FileUtils.readFileToString(confFile);

            final MultiLayerConfiguration confFromJson = MultiLayerConfiguration.fromJson(json);

            NeuralNetConfiguration conf2 = confFromJson.getConf(0);

            final MultiLayerNetwork net = new MultiLayerNetwork(confFromJson);
            net.init();
            net.setParameters(params);

            return Optional.of(net);

        } catch (IOException e) {
            e.printStackTrace();
        }

        return Optional.absent();
    }



}
