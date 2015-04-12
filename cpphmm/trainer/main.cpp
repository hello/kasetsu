#include <iostream>
#include "hmmfactory.h"
#include "input.h"
#include "trainer.h"

int main(int argc,const char * args[]) {

    if (argc <= 1) {
        std::cout << "need to specify input file of sensor data" << std::endl;
        return 0;
    }
    
    if (argc <= 2) {
        std::cout << "need to specify model from factory" << std::endl;
        return 0;
    }

    const std::string filename = args[1];
    const std::string model = args[2];
    
    
    
    HmmDataMatrix_t meas = parseCsvFileFromFile(filename);
    
    if (meas.empty()) {
        std::cout << "filename " << filename << " was empty." << std::endl;
        return 0;
    }
    
    
    HiddenMarkovModel * hmm = HmmFactory::getModel(model);
    
    if (hmm == NULL) {
        std::cout << "could not find model " << model << std::endl;
        return 0;
    }

    
    bool worked = Trainer::train(hmm,meas);

    delete hmm;
    hmm = NULL;

    return 0;
}
