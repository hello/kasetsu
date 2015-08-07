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

class DISABLED_TestMultiObsHmm : public TestMultiObsHmm {};

TEST_F(DISABLED_TestMultiObsHmm,TestUnlabeled) {
    
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
    
    UIntVec_t states1;
    HmmDataMatrix_t raw1;
    raw1.resize(1);
    raw1[0] = getAlphabetSignal(states1,n,A,alphabetProbs);
    
    UIntVec_t states2;
    HmmDataMatrix_t raw2;
    raw2.resize(1);
    raw2[0] = getAlphabetSignal(states2,n,A,alphabetProbs);
    
    UIntVec_t states3;
    HmmDataMatrix_t raw3;
    raw3.resize(1);
    raw3[0] = getAlphabetSignal(states3,n,A,alphabetProbs);
    
    TransitionMultiMap_t emptyForbiddenTransitions;
    LabelMap_t emptyLabels;
    
    
    MultiObsSequence multiObsSequence;
    multiObsSequence.addSequence(raw1,emptyForbiddenTransitions, emptyLabels);
    multiObsSequence.addSequence(raw2,emptyForbiddenTransitions, emptyLabels);
    multiObsSequence.addSequence(raw3,emptyForbiddenTransitions, emptyLabels);

    
    hmm.reestimate(multiObsSequence,20);
   
    HmmDataMatrix_t A2 = hmm.getAMatrix();
    HmmDataMatrix_t alphabet2 = hmm.getAlphabetMatrix();
    
    //TODO assert that A2 is near A, and the same for alphabet

    printMat("A2", A2);
    printMat("alphabet2", alphabet2);

}


TEST_F(TestMultiObsHmm,TestSemiSupervised) {

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
    int n2 = 50;

    LabelMap_t emptyLabels;
    
    UIntVec_t states1;
    LabelMap_t labels1;
    HmmDataMatrix_t raw1;
    raw1.resize(1);
    raw1[0] = getAlphabetSignal(states1,n2,A,alphabetProbs);
    
    for (int t = 0; t < states1.size(); t++) {
        labels1.insert(std::make_pair(t, states1[t]));
    }
    
    UIntVec_t states2;
    LabelMap_t labels2;
    HmmDataMatrix_t raw2;
    raw2.resize(1);
    raw2[0] = getAlphabetSignal(states2,n,A,alphabetProbs);
    
    UIntVec_t states3;
    LabelMap_t labels3;
    HmmDataMatrix_t raw3;
    raw3.resize(1);
    raw3[0] = getAlphabetSignal(states3,n,A,alphabetProbs);
    
    TransitionMultiMap_t emptyForbiddenTransitions;
    
    MultiObsSequence multiObsSequence;
    multiObsSequence.addSequence(raw1,emptyForbiddenTransitions, labels1);
    multiObsSequence.addSequence(raw2,emptyForbiddenTransitions, emptyLabels);
    multiObsSequence.addSequence(raw3,emptyForbiddenTransitions, emptyLabels);
    
    
    hmm.reestimate(multiObsSequence,5);
    
    HmmDataMatrix_t A2 = hmm.getAMatrix();
    HmmDataMatrix_t alphabet2 = hmm.getAlphabetMatrix();
    
    //TODO assert that A2 is near A, and the same for alphabet
    
    printMat("A2", A2);
    printMat("alphabet2", alphabet2);

}