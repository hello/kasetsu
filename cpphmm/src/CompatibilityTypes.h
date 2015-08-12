#ifndef _COMPATIBILITYTYPES_H_
#define _COMPATIBILITYTYPES_H_

#ifdef LINUX

#include <tr1/memory>
#include <tr1/unordered_set>
#include <tr1/unordered_map>

#define SHARED_PTR  std::tr1::shared_ptr
#define UNORDERED_SET std::tr1::unordered_set
#define UNORDERED_MAP std::tr1::unordered_map
#define UNORDERED_MULTIMAP std::tr1::unordered_multimap

#else

#include <memory>
#include <unordered_set>
#include <unordered_map>

#define SHARED_PTR  std::shared_ptr
#define UNORDERED_SET std::unordered_set
#define UNORDERED_MAP std::unordered_map
#define UNORDERED_MULTIMAP std::unordered_multimap

#endif



#endif //_COMPATIBILITYTYPES_H_
