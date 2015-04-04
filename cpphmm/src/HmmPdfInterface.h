#ifndef HMMPDFINTERFACE_H_
#define HMMPDFINTERFACE_H_

#include "HmmTypes.h"

class HmmPdfInterface {
public:
    virtual ~HmmPdfInterface() {};
    virtual HmmFloat_t getLogOfPdf(const HmmDataMatrix_t & x) = 0;
};

#endif //HMMPDFINTERFACE_H_
