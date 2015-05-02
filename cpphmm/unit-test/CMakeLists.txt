cmake_minimum_required (VERSION 2.8) 

PROJECT (HmmTests)

set(CMAKE_INCLUDE_PATH ${PROJECT_SOURCE_DIR}/)
set(CMAKE_MODULE_PATH ${PROJECT_SOURCE_DIR}/../cmake)

include_directories("../src/")

FIND_PACKAGE(gsl REQUIRED)
include_directories("${GSL_INCLUDE_DIR}")

#compile gtest
add_subdirectory("./gtest/" "${CMAKE_CURRENT_BINARY_DIR}/gtest" )

#compile algs
add_subdirectory("../src/" "${CMAKE_CURRENT_BINARY_DIR}/main")

#compile unit tests
include_directories("./gtest/include")

add_executable(unit-test
               main.cpp
               signalgenerator.cpp 
               testhmm.cpp
               testmodels.cpp)

target_link_libraries(unit-test gtest cpphmm ${GSL_LIBRARIES})

