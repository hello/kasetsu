#ifndef HMMPDFINTERFACE_H_
#define HMMPDFINTERFACE_H_

#include "HmmTypes.h"
#include <vector>
#include <string>
#include <memory>
#include <string.h>

class HmmPdfInterface;

typedef SHARED_PTR<HmmPdfInterface> HmmPdfInterfaceSharedPtr_t;

class HmmPdfInterface {
public:
    virtual ~HmmPdfInterface() {};
    virtual HmmDataVec_t getLogOfPdf(const HmmDataMatrix_t & x) const = 0;
    virtual HmmPdfInterfaceSharedPtr_t reestimate(const HmmDataVec_t & gammaForThisState, const HmmDataMatrix_t & meas, const HmmFloat_t eta) const = 0;
    virtual HmmPdfInterfaceSharedPtr_t clone(bool isPerturbed) const = 0;
    virtual uint32_t getNumberOfFreeParams() const = 0;

    virtual std::string serializeToJson() const = 0;
};

typedef std::vector<HmmPdfInterfaceSharedPtr_t> ModelVec_t;


#endif //HMMPDFINTERFACE_H_
