#include <string>
#include <json/json.h>
#include <iostream>
#include <fstream>


int main() {
    std::ifstream file("1012.json");
    
    if (!file.is_open()) {
        return -1;
    }
    
    Json::Reader reader;
    Json::Value top;
    
    if (!reader.parse(file, top)) {
        return -1;
    }
    
    int foo = 3;
    foo++;
    
    
    
    
  return 0;
}
