#ifndef _SERIALIZATIONHELPERS_H_
#define _SERIALIZATIONHELPERS_H_

#include <sstream>

template <class T>
class PassThroughSerializationAdapter {
public:
    std::string operator() (const T & t) const {
        std::stringstream ss;
        ss << t;
        return ss.str();
    }
};


template <class T,class Adaptor = PassThroughSerializationAdapter<typename T::value_type>  >
std::string vecToJsonArray(const T & vec) {
    std::stringstream myjson;
    myjson << "[";
    Adaptor adaptorFunctor;
    bool first = true;
    for (typename T::const_iterator it = vec.begin(); it != vec.end(); it++) {
        if (!first) {
            myjson << ",";
        }
        myjson << adaptorFunctor(*it);
        first = false;
    }
    myjson << "]";
    return myjson.str();
}

template <class T>
class PdfInterfaceSerializationAdapter {
public:
    std::string operator() (const T & t) const {
        return t->serializeToJson();
    }
};

template <class T>
class VecOfVecsSerializationAdapter {
public:
    std::string operator() (const T & t) const {
        return vecToJsonArray(t);
    }
};

std::string makeKeyValue(const std::string & key, const std::string & value);


#endif
