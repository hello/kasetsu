
#include "SerializationHelpers.h"
#include "HmmTypes.h"
std::string makeKeyValue(const std::string & key, const std::string & value) {
    std::stringstream ss;
    ss << "{\"" << key << "\" : " << value << "}";
    return ss.str();
}

