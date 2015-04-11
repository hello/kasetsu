#ifndef _INPUT_H_
#define _INPUT_H_

#include <sstream>
#include <string>
#include <vector>

#include "HmmTypes.h"


HmmDataMatrix_t parseCsvFile(std::istream& str);

HmmDataMatrix_t parseCsvFileFromFile(const std::string & filename);

#endif //_INPUT_H_
