#include "input.h"
#include <fstream>
typedef std::vector<std::string> StringVec_t;

StringVec_t getNextLineAndSplitIntoTokens(std::istream& str,int reserveNumber) {
    StringVec_t  result;
    std::string                line;
    std::getline(str,line);
    
    std::stringstream          lineStream(line);
    std::string                cell;
    
    result.reserve(reserveNumber);
    
    while(std::getline(lineStream,cell,',')) {
        result.push_back(cell);
    }
    
    return result;
}



HmmDataMatrix_t parseCsvFile(std::istream& str) {
    const int reserveNumber = 100000;
    StringVec_t res;
    HmmDataMatrix_t ret;
    
    while(1) {
        HmmDataVec_t vec;
        vec.reserve(reserveNumber);
        res = getNextLineAndSplitIntoTokens(str, reserveNumber);
        
        for (StringVec_t::const_iterator it = res.begin();
             it != res.end(); it++) {
            
            vec.push_back(atof((*it).c_str()));
            
        }
        
        if (res.empty()) {
            break;
        }
        
        ret.push_back(vec);
        
        
        
        
    };
    
    return ret;
}

HmmDataMatrix_t parseCsvFileFromFile(const std::string & filename) {
    HmmDataMatrix_t ret;
    std::ifstream file(filename);
    
    if (file.is_open()) {
        ret = parseCsvFile(file);
        file.close();
    }
    
    return ret;
}


