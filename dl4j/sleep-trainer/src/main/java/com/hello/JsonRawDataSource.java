package com.hello;

import com.fasterxml.jackson.annotation.JsonCreator;
import com.fasterxml.jackson.annotation.JsonProperty;
import com.fasterxml.jackson.core.type.TypeReference;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.google.common.base.Optional;
import com.google.common.collect.Maps;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.io.IOException;
import java.nio.charset.Charset;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

/**
 * Created by benjo on 12/8/15.
 */
public class JsonRawDataSource {
    final static ObjectMapper objectMapper = new ObjectMapper();
    final static Logger LOGGER = LoggerFactory.getLogger(JsonRawDataSource.class);

    public static class Item {

        @JsonProperty("data")
        final public Double [][] data;

        @JsonProperty("times")
        final public List<Long> times;

        @JsonCreator
        public Item(final Double [][] data,final List<Long> times ) {
            this.data = data;
            this.times = times;
        }

    }



    private static String readFile(String pathStr, Charset encoding) throws IOException {
        final Path path = Paths.get(pathStr);
        LOGGER.info(path.toString());
        byte[] encoded = Files.readAllBytes(path);
        return new String(encoded, encoding);
    }

    public static Map<String,Item> createFromFile(final String path) {
        try {
            final String contents = readFile(path, java.nio.charset.Charset.forName("UTF-8"));

            TypeReference<HashMap<String,Object>> typeRef
                    = new TypeReference<HashMap<String,Object>>() {};

            final Map<String,Item> dataSource = objectMapper.readValue(contents, typeRef);

            return dataSource;

        }
        catch (IOException e) {
            LOGGER.error(e.getMessage());
        }

        return Maps.newHashMap();
    }
}
