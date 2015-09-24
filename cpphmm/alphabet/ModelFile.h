#ifndef _MODELFILE_H_
#define _MODELFILE_H_

#include <string>
#include "../src/MultiObsSequenceHiddenMarkovModel.h"
#include "../src/HmmTypes.h"
#include <map>
#include "CommonTypes.h"




typedef std::multimap<std::string,MultiObsHmmSharedPtr_t> HmmMap_t;

class ModelFile {
public:
    static HmmMap_t LoadFile(const std::string & filename);
    static void SaveProtobuf(const HmmMap_t &hmms, const std::string &filename);

};

#endif //_MODELFILE_H_
