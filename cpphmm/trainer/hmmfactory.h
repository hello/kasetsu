#ifndef _HMMFACTORY_H_
#define _HMMFACTORY_H_

#include <string>

#include "HiddenMarkovModel.h"

class HmmFactory {
public:
    static HiddenMarkovModel * getModel(const std::string & modelname);
};
#endif //_HMMFACTORY_H_


