
#include "AllModels.h"


GammaModel::GammaModel() {
    
}
GammaModel::~GammaModel() {
    
}

HmmFloat_t GammaModel::getLogOfPdf(const HmmDataMatrix_t & x) {
    return 0.f;
}

///////////////////////////////////


PoissonModel::PoissonModel() {
    
}
PoissonModel::~PoissonModel() {
    
}

HmmFloat_t PoissonModel::getLogOfPdf(const HmmDataMatrix_t & x) {
    return 0.f;
}



///////////////////////////////////


AlphabetModel::AlphabetModel() {
    
}
AlphabetModel::~AlphabetModel() {
    
}

HmmFloat_t AlphabetModel::getLogOfPdf(const HmmDataMatrix_t & x) {
    return 0.f;
}
