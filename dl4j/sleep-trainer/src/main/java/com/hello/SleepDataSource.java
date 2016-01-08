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
import org.apache.commons.cli.Option;
import org.apache.commons.lang.ArrayUtils;
import org.deeplearning4j.datasets.iterator.DataSetIterator;
import org.nd4j.linalg.api.ndarray.INDArray;
import org.nd4j.linalg.dataset.DataSet;
import org.nd4j.linalg.dataset.api.DataSetPreProcessor;
import org.nd4j.linalg.factory.Nd4j;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.io.File;
import java.io.IOException;
import java.nio.charset.Charset;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.*;

/**
 * Created by benjo on 12/8/15.
 */
public class SleepDataSource implements DataSetIterator {
    final static ObjectMapper objectMapper = new ObjectMapper();
    final static Logger LOGGER = LoggerFactory.getLogger(SleepDataSource.class);
    final static TypeReference<HashMap<String,DataItem>> typeRef = new TypeReference<HashMap<String,DataItem>>() {};

    final static int INDEX_IN_BED = 1;
    final static int INDEX_SLEEP = 2;
    final static int INDEX_WAKE_UP = 3;
    final static int INDEX_OUT_OF_BED = 4;

    final static int NUM_LABELS = 3;

    final static Map<String,Integer> eventIndexMap;
    static {
        eventIndexMap = Maps.newHashMap();
        eventIndexMap.put("IN_BED",INDEX_IN_BED);
        eventIndexMap.put("SLEEP",INDEX_SLEEP);
        eventIndexMap.put("WAKE_UP",INDEX_WAKE_UP);
        eventIndexMap.put("OUT_OF_BED",INDEX_OUT_OF_BED);
    }

    public final List<DataSet> dataSets;
    public final List<INDArray> unusedFeatures;
    final int numInputs;
    final int numOutcomes;
    final int exampleLength;
    private final int miniBatchSize;
    int numExamplesSoFar;

    public DataSet next(final int n) {

        int endIdx = numExamplesSoFar + n;

        if (endIdx > dataSets.size()) {
            endIdx = dataSets.size();
        }

        final List<DataSet> dsList = Lists.newArrayList();
        for (int i = numExamplesSoFar; i < endIdx; i++) {
            dsList.add(dataSets.get(i));
        }

        numExamplesSoFar += n;

        final DataSet ds = DataSet.merge(dsList);

        return ds;
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

        Collections.shuffle(dataSets);

    }

    public int batch() {
        return miniBatchSize;
    }

    public int cursor() {
        return numExamplesSoFar;
    }

    public int numExamples() {
        return dataSets.size();
    }

    public void setPreProcessor(DataSetPreProcessor dataSetPreProcessor) {

    }

    @Override
    public List<String> getLabels() {
        return Collections.EMPTY_LIST;
    }

    public boolean hasNext() {
        return numExamplesSoFar < dataSets.size();
    }

    public DataSet next() {
        return next(miniBatchSize);
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

    private static INDArray getFeatures( final DataItem sensorData) {
        double [][] primitiveDataArray = new double[sensorData.data.length][];
        for (int j = 0; j < primitiveDataArray.length; j++) {
            primitiveDataArray[j] = ArrayUtils.toPrimitive(sensorData.data[j]);
        }

        final INDArray primitiveDataAsInput = Nd4j.create(primitiveDataArray).transpose();
        final INDArray features = Nd4j.create(Lists.<INDArray>newArrayList(primitiveDataAsInput),new int[]{1,primitiveDataAsInput.size(0),primitiveDataAsInput.size(1)});

        return features;
    }

    private static Optional<DataSet> getDataSet(final Collection<LabelItem> labelData, final DataItem sensorData ) {
        //Data: has shape [miniBatchSize,nIn,timeSeriesLength];

        final int vecSize = sensorData.data[0].length;
        final int numTimeSteps = sensorData.data.length;
        final long t0 = sensorData.times.get(0);
        final long tf = sensorData.times.get(sensorData.times.size() - 1);


        //zeros because an all zero label will have no effect on the cross entropy objective function evaluation
        final INDArray input = getFeatures(sensorData);
        final INDArray labels = Nd4j.zeros(new int[]{1,NUM_LABELS,numTimeSteps});

        LabelItem sleepLabel = null;
        LabelItem wakeLabel = null;
        for (final LabelItem label : labelData) {
            if (label.eventIndex == INDEX_SLEEP) {
                sleepLabel = label;
            }

            if (label.eventIndex == INDEX_WAKE_UP) {
                wakeLabel = label;
            }
        }

        if (sleepLabel == null || wakeLabel == null) {
            return Optional.absent();
        }


        final int idxSleep =(int) ((sleepLabel.timestamp - t0) / (5L * 60L));
        final int idxWake =(int) ((wakeLabel.timestamp - t0) / (5L * 60L));
        final int idxEnd = (int) ((tf - t0) / (5L * 60L));

        for (int t = 0; t < idxSleep; t++) {
            labels.putScalar(new int[]{0,0,t},1.0);

        }

        for (int t = idxSleep; t < idxWake; t++) {
            labels.putScalar(new int[]{0,1,t},1.0);

        }

        for (int t = idxWake; t <= idxEnd; t++) {
            labels.putScalar(new int[]{0,2,t},1.0);
        }


        return Optional.of(new DataSet(input,labels));
    }

    private SleepDataSource(final Map<String, DataItem> dataMap, final Multimap<String,LabelItem> labelMap, final int miniBatchSize) {
        dataSets = Lists.newArrayList();
        unusedFeatures = Lists.newArrayList();

        this.miniBatchSize = miniBatchSize;

        for (final String key : dataMap.keySet()) {

            final DataItem data = dataMap.get(key);

            if (!labelMap.containsKey(key)) {
                //not labeled? add to data set
                unusedFeatures.add(getFeatures(data));
                continue;
            }

            final Collection<LabelItem> labels = labelMap.get(key);

            if (labels.isEmpty()) {
                continue;
            }


            final Optional<DataSet> ds = getDataSet(labels,data);

            if (ds.isPresent()) {
                dataSets.add(ds.get());
            }
            else {
                unusedFeatures.add(getFeatures(data));
            }

        }

        reset();

        if (dataSets.isEmpty()) {
            exampleLength = unusedFeatures.get(0).size(2);
            numInputs = unusedFeatures.get(0).size(1);
            numOutcomes = NUM_LABELS;
            numExamplesSoFar = 0;
        }
        else {
            exampleLength = dataSets.get(0).numExamples();
            numInputs = dataSets.get(0).getFeatureMatrix().size(1);
            numOutcomes = dataSets.get(0).getLabels().size(1);
            numExamplesSoFar = 0;
        }



    }

    private static String readFile(String pathStr, Charset encoding) throws IOException {
        final Path path = Paths.get(pathStr);
        LOGGER.info(path.toString());
        byte[] encoded = Files.readAllBytes(path);
        return new String(encoded, encoding);
    }

    public static Optional<SleepDataSource> createFromFile(final String rawDataFilePath) {
        return createFromFile(rawDataFilePath,"",0);
    }

    public static Optional<SleepDataSource> createFromFile(final String rawDataFilePath, final String csvLabelsPath, final int miniBatchSize) {
        try {

            final File rawDataFile = new File(SleepDataSource.class.getClassLoader().getResource(rawDataFilePath).getFile());
            final File labelFile = new File(SleepDataSource.class.getClassLoader().getResource(csvLabelsPath).getFile());

            final String jsonFileContents = readFile(rawDataFile.getAbsolutePath(), java.nio.charset.Charset.forName("UTF-8"));

            final Map<String,DataItem> dataMap = objectMapper.readValue(jsonFileContents, typeRef);

            String labelFileContents = "";
            if (!csvLabelsPath.isEmpty()) {
                labelFileContents = readFile(labelFile.getAbsolutePath(), java.nio.charset.Charset.forName("UTF-8"));
            }

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

            return Optional.of(new SleepDataSource(dataMap, labelMap,miniBatchSize));

        }
        catch (IOException e) {
            LOGGER.error(e.getMessage());
        }

        return Optional.absent();
    }
}
