#ifndef HMMPDFINTERFACE_H_
#define HMMPDFINTERFACE_H_

#include "HmmTypes.h"
#include <vector>
#include <string>

class HmmPdfInterface {
public:
    virtual ~HmmPdfInterface() {};
    virtual HmmDataVec_t getLogOfPdf(const HmmDataMatrix_t & x) const = 0;
    virtual HmmPdfInterface * reestimate(const HmmDataVec_t & gammaForThisState, const HmmDataMatrix_t & meas) const = 0;
    virtual HmmPdfInterface * clone(bool isPerturbed) const = 0;

    virtual std::string serializeToJson() const = 0;
};

typedef std::vector<HmmPdfInterface *> ModelVec_t;


#endif //HMMPDFINTERFACE_H_
