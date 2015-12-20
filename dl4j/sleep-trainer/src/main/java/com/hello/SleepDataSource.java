package com.hello;

import com.fasterxml.jackson.annotation.JsonCreator;
import com.fasterxml.jackson.annotation.JsonProperty;
import com.fasterxml.jackson.core.type.TypeReference;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.google.common.base.Optional;
import com.google.common.collect.ArrayListMultimap;
import com.google.common.collect.Lists;
import com.google.common.collect.Maps;
import com.google.common.collect.Multimap;
import org.apache.commons.lang.ArrayUtils;
import org.deeplearning4j.datasets.iterator.DataSetIterator;
import org.nd4j.linalg.api.ndarray.INDArray;
import org.nd4j.linalg.dataset.DataSet;
import org.nd4j.linalg.dataset.api.DataSetPreProcessor;
import org.nd4j.linalg.factory.Nd4j;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.io.IOException;
import java.nio.charset.Charset;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.Collection;
import java.util.HashMap;
import java.util.Iterator;
import java.util.LinkedList;
import java.util.List;
import java.util.Map;

/**
 * Created by benjo on 12/8/15.
 */
public class SleepDataSource implements DataSetIterator {
    final static ObjectMapper objectMapper = new ObjectMapper();
    final static Logger LOGGER = LoggerFactory.getLogger(SleepDataSource.class);
    final static TypeReference<HashMap<String,DataItem>> typeRef = new TypeReference<HashMap<String,DataItem>>() {};

    final static int INDEX_IN_BED = 0;
    final static int INDEX_SLEEP = 1;
    final static int INDEX_WAKE_UP = 2;
    final static int INDEX_OUT_OF_BED = 3;

    final static int NUM_LABELS = 4;

    final static Map<String,Integer> eventIndexMap;
    static {
        eventIndexMap = Maps.newHashMap();
        eventIndexMap.put("IN_BED",INDEX_IN_BED);
        eventIndexMap.put("SLEEP",INDEX_SLEEP);
        eventIndexMap.put("WAKE_UP",INDEX_WAKE_UP);
        eventIndexMap.put("OUT_OF_BED",INDEX_OUT_OF_BED);
    }

    final List<DataSet> dataSets;
    final int numInputs;
    final int numOutcomes;
    final int exampleLength;
    int numExamplesSoFar;

    public DataSet next(final int n) {

        final List<DataSet> dsList = Lists.newArrayList();
        for (int i = numExamplesSoFar; i < numExamplesSoFar + n; i++) {
            dsList.add(dataSets.get(i));
        }

        return  DataSet.merge(dsList);
    }

    public int totalExamples() {
        return dataSets.size();
    }

    public int inputColumns() {
        return numInputs;
    }

    public int totalOutcomes() {
        return numOutcomes;
    }

    public void reset() {
        numExamplesSoFar = 0;
    }

    public int batch() {
        return exampleLength;
    }

    public int cursor() {
        return numExamplesSoFar;
    }

    public int numExamples() {
        return dataSets.size();
    }

    public void setPreProcessor(DataSetPreProcessor dataSetPreProcessor) {

    }

    public boolean hasNext() {
        return numExamplesSoFar < dataSets.size();
    }

    public DataSet next() {
        return next(1);
    }

    public void remove() {

    }

    public static class DataItem {

        @JsonProperty("data")
        final public Double [][] data;

        @JsonProperty("times")
        final public List<Long> times;

        @JsonCreator
        public DataItem(@JsonProperty("data") final Double[][] data,@JsonProperty("times") final List<Long> times) {
            this.data = data;
            this.times = times;
        }

    }

    public static class LabelItem {
        public final int eventIndex;

        public final long timestamp;


        public LabelItem(int eventIndex, long timestamp) {
            this.eventIndex = eventIndex;
            this.timestamp = timestamp;
        }
    }

    private static DataSet getDataSet(final Collection<LabelItem> labelData, final DataItem sensorData ) {

        final int vecSize = sensorData.data[0].length;
        final int numTimeSteps = sensorData.data.length;
        final long t0 = sensorData.times.get(0);

        double [][] primitiveDataArray = new double[sensorData.data.length][];
        for (int j = 0; j < primitiveDataArray.length; j++) {
            primitiveDataArray[j] = ArrayUtils.toPrimitive(sensorData.data[j]);
        }

        final INDArray input = Nd4j.create(new int[]{1, numTimeSteps,vecSize}, primitiveDataArray);

        //zeros because an all zero label will have no effect on the cross entropy objective function evaluation
        final INDArray labels = Nd4j.zeros(new int[]{1,numTimeSteps,NUM_LABELS});

        for (final LabelItem label : labelData) {
            final int idx =(int) ((label.timestamp - t0) / (5L * 60L));

            if (idx < 0 || idx >= numTimeSteps) {
                continue;
            }

            int startIdx = idx - 12;

            if (startIdx < 0) {
                startIdx = 0;
            }

            int endIdx = idx + 12;

            if (endIdx > numTimeSteps) {
                endIdx = numTimeSteps;
            }

            for (int t = startIdx; t < endIdx; t++) {
                labels.putScalar(new int[]{0,t,label.eventIndex},1.0);
            }
        }

        return new DataSet(input,labels);
    }

    private SleepDataSource(final Map<String, DataItem> dataMap, final Multimap<String,LabelItem> labelMap) {
        dataSets = Lists.newArrayList();

        for (final String key : dataMap.keySet()) {
            if (!labelMap.containsKey(key)) {
                continue;
            }

            final Collection<LabelItem> labels = labelMap.get(key);
            final DataItem data = dataMap.get(key);

            if (labels.isEmpty()) {
                continue;
            }


            dataSets.add(getDataSet(labels, data));

        }

        reset();

        exampleLength = dataSets.get(0).numExamples();
        numInputs = dataSets.get(0).numInputs();
        numOutcomes = dataSets.get(0).numOutcomes();
        numExamplesSoFar = 0;


    }

    private static String readFile(String pathStr, Charset encoding) throws IOException {
        final Path path = Paths.get(pathStr);
        LOGGER.info(path.toString());
        byte[] encoded = Files.readAllBytes(path);
        return new String(encoded, encoding);
    }

    public static Optional<SleepDataSource> createFromFile(final String pathToJsonRawData, final String pathToCsvLabels) {
        try {
            final String jsonFileContents = readFile(pathToJsonRawData, java.nio.charset.Charset.forName("UTF-8"));

            final Map<String,DataItem> dataMap = objectMapper.readValue(jsonFileContents, typeRef);

            final String labelFileContents = readFile(pathToCsvLabels, java.nio.charset.Charset.forName("UTF-8"));

            final Multimap<String,LabelItem> labelMap = ArrayListMultimap.create();

            final String [] lines = labelFileContents.split("\n");

            boolean first = true;
            for (final String line : lines) {
                if (first) {
                    //skip header
                    first = false;
                    continue;
                }

                final String [] items = line.trim().split(",");

                if (items.length < 3) {
                    continue;
                }

                final String eventType = items[1];

                if (!eventIndexMap.containsKey(eventType)) {
                    continue;
                }

                final Long timestampLocalUtc = Long.valueOf(items[2]);

                if (timestampLocalUtc == null) {
                    continue;
                }

                labelMap.put(items[0],new LabelItem(eventIndexMap.get(eventType),timestampLocalUtc));

            }

            return Optional.of(new SleepDataSource(dataMap, labelMap));

        }
        catch (IOException e) {
            LOGGER.error(e.getMessage());
        }

        return Optional.absent();
    }
}
