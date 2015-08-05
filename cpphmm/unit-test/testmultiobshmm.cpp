//
//  testmultiobshmm.cpp
//  HmmTests
//
//  Created by Benjamin Joseph on 8/4/15.
//
//
#include "gtest/gtest.h"
#include "signalgenerator.h"
#include "../src/MultiObsSequenceHiddenMarkovModel.h"
#include "../src/MatrixHelpers.h"

class TestMultiObsHmm : public ::testing::Test {
protected:
    virtual void SetUp() {
        
    }
    
    virtual void TearDown() {
        
    }
    
    
};

TEST_F(TestMultiObsHmm,TestFoo) {
    
    HmmDataMatrix_t alphabetProbs;
    alphabetProbs.resize(2);
    alphabetProbs[0] << 0.8,0.1,0.1;
    alphabetProbs[1] << 0.1,0.1,0.8;
    
    
    HmmDataMatrix_t alphabetProbsInit;
    alphabetProbsInit.resize(2);
    alphabetProbsInit[0] << 0.5,0.25,0.25;
    alphabetProbsInit[1] << 0.3,0.3,0.4;
    

    
    HmmDataMatrix_t A;
    A.resize(2);
    A[0] << 0.8,0.2;
    A[1] << 0.2,0.8;
    
    
    HmmDataMatrix_t Ainit;
    Ainit.resize(2);
    Ainit[0] << 0.99,0.01;
    Ainit[1] << 0.01,0.99;
    
    
    
    
    MultiObsHiddenMarkovModel hmm(alphabetProbsInit,Ainit);
    int n = 1000;
    HmmDataMatrix_t raw1;
    raw1.resize(1);
    raw1[0] = getAlphabetSignal(n,A,alphabetProbs);
    
    HmmDataMatrix_t raw2;
    raw2.resize(1);
    raw2[0] = getAlphabetSignal(n,A,alphabetProbs);
    
    HmmDataMatrix_t raw3;
    raw3.resize(1);
    raw3[0] = getAlphabetSignal(n,A,alphabetProbs);
    
    TransitionMultiMap_t emptyForbiddenTransitions;
    LabelMap_t emptyLabels;
    
    
    MultiObsSequence multiObsSequence;
    multiObsSequence.addSequence(raw1,emptyForbiddenTransitions, emptyLabels);
    multiObsSequence.addSequence(raw2,emptyForbiddenTransitions, emptyLabels);
    multiObsSequence.addSequence(raw3,emptyForbiddenTransitions, emptyLabels);

    
    hmm.reestimate(multiObsSequence);
   
    HmmDataMatrix_t A2 = hmm.getAMatrix();
    HmmDataMatrix_t alphabet2 = hmm.getAlphabetMatrix();
    
    printMat("A2", A2);
    
    printMat("alphabet2", alphabet2);
    
    
}