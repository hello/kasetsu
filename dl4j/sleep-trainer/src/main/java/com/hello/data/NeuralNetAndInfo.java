package com.hello.data;

import org.deeplearning4j.nn.conf.MultiLayerConfiguration;
import org.deeplearning4j.nn.multilayer.MultiLayerNetwork;

/**
 * Created by benjo on 2/21/16.
 */
public class NeuralNetAndInfo {
    final public MultiLayerNetwork net;

    public NeuralNetAndInfo(MultiLayerNetwork net, MultiLayerConfiguration conf) {
        this.net = net;
        this.conf = conf;
    }

    final public MultiLayerConfiguration conf;
}
