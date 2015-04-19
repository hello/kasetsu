#include <iostream>
#include "hmmfactory.h"
#include "input.h"
#include "trainer.h"
#include <memory>
#include <fstream>


int main(int argc,const char * args[]) {

    if (argc <= 1) {
        std::cout << "need to specify input file of sensor data" << std::endl;
        return 0;
    }
    
    if (argc <= 2) {
        std::cout << "need to specify model from factory" << std::endl;
        return 0;
    }
    
    if (argc <= 3) {
        std::cout << "need to output file" << std::endl;
        return 0;
    }

    const std::string filename = args[1];
    const std::string model = args[2];
    const std::string outputfilename = args[3];
    
    
    HmmDataMatrix_t meas = parseCsvFileFromFile(filename);
    
    if (meas.empty()) {
        std::cout << "filename " << filename << " was empty." << std::endl;
        return 0;
    }
    
    
    std::unique_ptr<HiddenMarkovModel> hmm(HmmFactory::getModel(model));
    
    if (hmm.get() == NULL) {
        std::cout << "could not find model " << model << std::endl;
        return 0;
    }

    
    bool worked = Trainer::train(hmm.get(),meas);
    
    if (!worked) {
        return 0;
    }

    std::ofstream outfile(outputfilename);
    
    if (outfile.is_open()) {
        outfile <<  hmm.get()->serializeToJson();
        outfile.close();
    }
    
    
    return 0;
}
