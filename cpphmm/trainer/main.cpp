#include <iostream>
#include "hmmfactory.h"
#include "input.h"
#include "trainer.h"
#include <fstream>
#include <stdlib.h>     /* srand, rand */
#include <time.h>       /* time */
#include "CompatibilityTypes.h"

class FileStateSaver : public SaveStateInterface {
public:
    FileStateSaver(const std::string & filename) : _filename(filename){
        
    }
    
    void saveState (const std::string & data) {
        std::ofstream outfile;
        outfile.open(_filename.c_str());
        
        if (outfile.is_open()) {
            outfile <<  data;
            outfile.close();
        }
    }
    
private:
    std::string _filename;
};

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
    
    if (argc <= 4) {
        std::cout << "need max iters" << std::endl;
        return 0;
    }
    
    srand (time(NULL));
 
    const std::string filename = args[1];
    const std::string model = args[2];
    const std::string outputfilename = args[3];
    const std::string maxiterstr = args[4];
    const int maxiter = atoi(maxiterstr.c_str());
    
    
    HmmDataMatrix_t meas = parseCsvFileFromFile(filename);
    
    if (meas.empty()) {
        std::cout << "filename " << filename << " was empty." << std::endl;
        return 0;
    }
    
    FileStateSaver saver(outputfilename);

    
    HmmSharedPtr_t hmm(HmmFactory::getModel(model,meas,&saver));
    
    if (hmm.get() == NULL) {
        std::cout << "could not find model " << model << std::endl;
        return 0;
    }

    std::cout << "There are " << meas[0].size() << " data points." << std::endl;
    bool worked = false;
    
    
    if (model == "seed" || model == "partnerseed" || model == "light" || model == "motion") {
        worked = Trainer::grow(hmm.get(),meas,maxiter);
    }
    else {
        worked = Trainer::train(hmm.get(),meas,maxiter);
    }
    
    std::ofstream outfile;
    outfile.open(outputfilename.c_str());
    
    if (outfile.is_open()) {
        outfile <<  hmm.get()->serializeToJson();
        outfile.close();
    }
    
    
    return 0;
}
