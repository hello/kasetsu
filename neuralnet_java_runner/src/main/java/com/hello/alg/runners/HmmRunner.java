package com.hello.alg.runners;

import com.google.common.base.Optional;
import com.hello.alg.helpers.CsvUtils;
import com.hello.suripu.algorithm.hmm.HmmDecodedResult;

import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Paths;

/**
 * Created by benjo on 11/2/16.
 */
public class HmmRunner {


    public static void main(String [] args ) throws IOException {

        //data should be of the format [numSensors x numTimeSteps]
        final double [][] data  = CsvUtils.csvToDoubles(CsvUtils.getFileContents(args[0]));

        Optional<HmmModel> hmmOptional = HmmModelFactory.getModelById(args[1]);

        if (!hmmOptional.isPresent()) {
            //todo error message
            return;
        }

        HmmModel model  = hmmOptional.get();

        final HmmDecodedResult result = model.hmm.decode(data,model.possibleEndStates,model.minLikelihood);


        //this is the sequence of states given the model and the data result.bestPath;


    }

}
