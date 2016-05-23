cmake_minimum_required (VERSION 2.8) 

PROJECT (TinyLstm)

set(CMAKE_INCLUDE_PATH ${PROJECT_SOURCE_DIR}/)
set(CMAKE_MODULE_PATH ${PROJECT_SOURCE_DIR}/cmake)

find_package(SndFile REQUIRED)

add_definitions(-DUSE_CPP_DEBUG_LOGGING)
add_definitions(-DNO_EQUALIZATION)

include_directories (${SNDFILE_INCLUDE_DIRS})

message(STATUS "${SNDFILE_INCLUDE_DIRS}")
message(STATUS "${SNDFILE_LIBRARIES}")


add_executable(tinylstm
tinylstm.cpp 
tinylstm_math.c 
tinylstm_net.c
tinylstm_tensor.c)

target_link_libraries(tinylstm ${SNDFILE_LIBRARIES})

