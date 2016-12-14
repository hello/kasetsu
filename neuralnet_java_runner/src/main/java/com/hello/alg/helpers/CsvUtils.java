package com.hello.alg.helpers;

import com.google.common.collect.Maps;
import com.google.common.collect.Multimap;
import com.hello.suripu.core.algorithmintegration.OneDaysSensorData;

import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Paths;
import java.util.Map;

/**
 * Created by benjo on 12/9/16.
 */
public class CsvUtils {

    public static double [][] csvToDoubles(final String fileContents) {
        final String [] lines = fileContents.split("\n");
        int N = lines.length;

        if (lines[N-1].length() <= 1) {
            N--;
        }

        double [][] arr = new double[N][];

        for (int irow = 0; irow < N; irow++) {

            final String [] elements = lines[irow].split(",");
            final double [] row = new double[elements.length];

            for (int i = 0; i < elements.length; i++) {
                row[i] = Double.valueOf(elements[i].trim()).doubleValue();
            }

            arr[irow] = row;

        }

        return arr;
    }




    public static String getFileContents(final String filename) throws IOException {
        return new String(Files.readAllBytes(Paths.get(filename)));
    }
}
