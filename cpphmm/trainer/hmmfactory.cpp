#include "hmmfactory.h"
#include <string>




static HiddenMarkovModel * getDefaultModel() {
    const int num_states = 11;
    
    HmmDataMatrix_t A;
    
    
    HiddenMarkovModel * model = new HiddenMarkovModel(A);
    
    return model;
}


HiddenMarkovModel * HmmFactory::getModel(const std::string & modelname) {
    if (modelname == "default") {
        return getDefaultModel();
    }
    

    return NULL;

}
