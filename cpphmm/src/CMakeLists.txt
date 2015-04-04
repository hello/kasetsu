cmake_minimum_required (VERSION 2.8) 

project(CppHmmLibrary)


add_definitions(-DUSE_CPP_DEBUG_LOGGING)

include_directories ("${PROJECT_SOURCE_DIR}")


#compile our alg code
add_library(cpphmm STATIC
HiddenMarkovModel.cpp
AllModels.cpp
CompositeModel.cpp
)


