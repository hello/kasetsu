cmake_minimum_required (VERSION 2.8) 

PROJECT (TinyLstm)

set(CMAKE_OSX_DEPLOYMENT_TARGET "10.10")

set(CMAKE_INCLUDE_PATH ${PROJECT_SOURCE_DIR}/)
set(CMAKE_MODULE_PATH ${PROJECT_SOURCE_DIR}/cmake)


find_package(SndFile REQUIRED)

add_definitions(-DUSE_CPP_DEBUG_LOGGING)
add_definitions(-DNO_EQUALIZATION)

include_directories (${SNDFILE_INCLUDE_DIRS} "gtest/include/" "gtest")

message(STATUS "${SNDFILE_INCLUDE_DIRS}")
message(STATUS "${SNDFILE_LIBRARIES}")

add_library(gtest STATIC gtest/gtest-all.cc)
add_executable(unit-test unit-test/main.cpp unit-test/test1.cpp)
target_link_libraries(unit-test gtest)

add_executable(tinylstm
tinylstm.cpp 
tinylstm_math.c 
tinylstm_net.c
tinylstm_tensor.c
tinylstm_conv_layer.c
)

target_link_libraries(tinylstm ${SNDFILE_LIBRARIES})

