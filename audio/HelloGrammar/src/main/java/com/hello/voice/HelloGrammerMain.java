package com.hello.voice;
import java.io.File;
import java.io.FileInputStream;
import java.io.InputStream;

import edu.cmu.sphinx.api.Configuration;
import edu.cmu.sphinx.api.SpeechResult;
import edu.cmu.sphinx.api.StreamSpeechRecognizer;

/**
 * Created by benjo on 10/30/16.
 */
public class HelloGrammerMain {

    private static final String GRAMMAR_PATH = HelloGrammerMain.class.getResource("test.jsg").toString();

    public static void main(String[] args) throws Exception {

        final File grammarLocation = new File("src/main/resources/");

        final Configuration configuration = new Configuration();


        configuration.setAcousticModelPath("resource:/edu/cmu/sphinx/models/en-us/en-us");
        configuration.setDictionaryPath("resource:/edu/cmu/sphinx/models/en-us/cmudict-en-us.dict");

        //configuration.setLanguageModelPath("resource:/edu/cmu/sphinx/models/en-us/en-us.lm.bin");
        configuration.setUseGrammar(true);
        configuration.setGrammarName("test");
        configuration.setGrammarPath(grammarLocation.getAbsolutePath());
        configuration.setSampleRate(16000);

        StreamSpeechRecognizer recognizer = new StreamSpeechRecognizer(configuration);

        final InputStream stream = new FileInputStream(new File("/Users/benjo/Desktop/test2.wav"));

        recognizer.startRecognition(stream);
        SpeechResult result;
        while ((result = recognizer.getResult()) != null) {
            System.out.format("Hypothesis: %s\n", result.getHypothesis());
        }
        recognizer.stopRecognition();
    }

}
