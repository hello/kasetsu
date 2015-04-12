cmake_minimum_required (VERSION 2.8) 

project(CppHmmLibrary)

set(CMAKE_MODULE_PATH ${PROJECT_SOURCE_DIR}/../cmake)
set("CMAKE_CXX_FLAGS" "${CMAKE_CXX_FLAGS} -Wall -Werror -std=c++11 -stdlib=libc++")

add_definitions(-DUSE_CPP_DEBUG_LOGGING)

FIND_PACKAGE(gsl REQUIRED)
include_directories("${GSL_INCLUDE_DIR}")

include_directories ("${PROJECT_SOURCE_DIR}")


#compile our alg code
add_library(cpphmm STATIC
HiddenMarkovModel.cpp
AllModels.cpp
CompositeModel.cpp
ReestimationResult.cpp
)

target_link_libraries(cpphmm ${GSL_LIBRARIES})
