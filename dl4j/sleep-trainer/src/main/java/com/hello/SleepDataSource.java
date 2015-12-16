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
import org.deeplearning4j.datasets.iterator.DataSetIterator;
import org.nd4j.linalg.dataset.DataSet;
import org.nd4j.linalg.dataset.api.DataSetPreProcessor;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.io.IOException;
import java.nio.charset.Charset;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.Collection;
import java.util.HashMap;
import java.util.LinkedList;
import java.util.List;
import java.util.Map;

/**
 * Created by benjo on 12/8/15.
 */
public class SleepDataSource implements DataSetIterator {
    final static ObjectMapper objectMapper = new ObjectMapper();
    final static Logger LOGGER = LoggerFactory.getLogger(SleepDataSource.class);
    final static TypeReference<HashMap<String,Object>> typeRef = new TypeReference<HashMap<String,Object>>() {};

    final static Map<String,Integer> eventIndexMap;
    static {
        eventIndexMap = Maps.newHashMap();
        eventIndexMap.put("IN_BED",1);
        eventIndexMap.put("SLEEP",2);
        eventIndexMap.put("WAKE_UP",3);
        eventIndexMap.put("OUT_OF_BED",4);
    }

    final List<DataSet> dataSets;

    public DataSet next(int i) {
        return null;
    }

    public int totalExamples() {
        return 0;
    }

    public int inputColumns() {
        return 0;
    }

    public int totalOutcomes() {
        return 0;
    }

    public void reset() {

    }

    public int batch() {
        return 0;
    }

    public int cursor() {
        return 0;
    }

    public int numExamples() {
        return 0;
    }

    public void setPreProcessor(DataSetPreProcessor dataSetPreProcessor) {

    }

    public boolean hasNext() {
        return false;
    }

    public DataSet next() {
        return null;
    }

    public void remove() {

    }

    public static class DataItem {

        @JsonProperty("data")
        final public Double [][] data;

        @JsonProperty("times")
        final public List<Long> times;

        @JsonCreator
        public DataItem(final Double[][] data, final List<Long> times) {
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


    private SleepDataSource(final Map<String, DataItem> dataMap, final Multimap<String,LabelItem> labelMap) {
        dataSets = Lists.newArrayList();

        for (final String key : dataMap.keySet()) {
            if (!labelMap.containsKey(key)) {
                continue;
            }

            final Collection<LabelItem> labels = labelMap.get(key);
            final DataItem data = dataMap.get(key);

            //turn this into a data set... basically, map label to index.
            //need scheme for this!  null labels?  gah.  weighed labels?

        }
        //initialize the linked list
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
