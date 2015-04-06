cmake_minimum_required (VERSION 2.8) 

PROJECT (HmmTests)

set(CMAKE_INCLUDE_PATH ${PROJECT_SOURCE_DIR}/)
include_directories("../src/")



#compile gtest
add_subdirectory("./gtest/" "${CMAKE_CURRENT_BINARY_DIR}/gtest" )

#compile algs
add_subdirectory("../src/" "${CMAKE_CURRENT_BINARY_DIR}/main")

#compile unit tests
include_directories("./gtest/include")

add_executable(unit-test
               main.cpp 
               testhmm.cpp
               testmodels.cpp)

target_link_libraries(unit-test gtest cpphmm)

