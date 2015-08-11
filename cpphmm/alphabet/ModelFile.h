#ifndef _MODELFILE_H_
#define _MODELFILE_H_

#include <string>
#include "../src/MultiObsSequenceHiddenMarkovModel.h"
#include "../src/HmmTypes.h"


class ModelFile {
public:
    static MultiObsHiddenMarkovModel * LoadFile(const std::string & filename);
    static void SaveFile(const MultiObsHiddenMarkovModel & hmm,const std::string & filename);
};

#endif //_MODELFILE_H_
