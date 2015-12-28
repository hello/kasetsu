package com.hello;

import com.google.common.base.Optional;
import org.apache.commons.io.FileUtils;
import org.deeplearning4j.eval.Evaluation;
import org.deeplearning4j.nn.conf.MultiLayerConfiguration;
import org.deeplearning4j.nn.conf.NeuralNetConfiguration;
import org.deeplearning4j.nn.multilayer.MultiLayerNetwork;
import org.nd4j.linalg.api.ndarray.INDArray;
import org.nd4j.linalg.factory.Nd4j;
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

        final Optional<SleepDataSource> dataOptional = SleepDataSource.createFromFile(dataFilename);

        if (!dataOptional.isPresent()) {
            LOGGER.error("failed to load data sources");
            return;
        }

        final Optional<MultiLayerNetwork> networkOptional = loadNet(netFilename);

        if (!networkOptional.isPresent()) {
            LOGGER.error("failed to load network {}",netFilename);
            return;
        }

        final MultiLayerNetwork net = networkOptional.get();


        for (final INDArray feats : dataOptional.get().unusedFeatures) {
            final INDArray output = net.output(feats);
            LOGGER.info(output.slice(0).transpose().toString());
            LOGGER.info("----");

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
