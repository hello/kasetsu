package com.hello.voice;
import java.io.File;
import java.io.FileInputStream;
import java.io.InputStream;

import edu.cmu.sphinx.api.Configuration;
import edu.cmu.sphinx.api.LiveSpeechRecognizer;
import edu.cmu.sphinx.api.SpeechResult;
import edu.cmu.sphinx.api.StreamSpeechRecognizer;

/**
 * Created by benjo on 10/30/16.
 */
public class HelloGrammerMain {


    public static void main(String[] args) throws Exception {

        final File grammarLocation = new File(args[0]);

        final Configuration configuration = new Configuration();

        configuration.setAcousticModelPath("resource:/edu/cmu/sphinx/models/en-us/en-us");
        configuration.setDictionaryPath("resource:/edu/cmu/sphinx/models/en-us/cmudict-en-us.dict");

        configuration.setUseGrammar(true);
        configuration.setGrammarName("hello");
        configuration.setGrammarPath(grammarLocation.getAbsolutePath());
        configuration.setSampleRate(16000);

        final StreamSpeechRecognizer recognizer = new StreamSpeechRecognizer(configuration);

        recognizer.startRecognition(new FileInputStream(args[1]));

        SpeechResult result = null;

        while ((result = recognizer.getResult()) != null) {
            System.out.println(result.getHypothesis());
        }

    }

}
