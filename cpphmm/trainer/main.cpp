#include <iostream>
#include "hmmfactory.h"

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
    
    
    const HiddenMarkovModel * hmm = HmmFactory::getModel(model);
    
    if (hmm == NULL) {
        std::cout << "could not find model " << model << std::endl;
        return 0;
    }
    
    
    
    /* TODO 
     
     1) load up data vector from file
     2) add model creation to factory
     3) generate model json file or protobuf file so we can plot in python
     
     */
    
    
    
    delete hmm;
    hmm = NULL;

    return 0;
}
