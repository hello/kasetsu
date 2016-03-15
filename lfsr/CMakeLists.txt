cmake_minimum_required (VERSION 2.8)

PROJECT (PnGenerator)

set(CMAKE_INCLUDE_PATH ${PROJECT_SOURCE_DIR}/)
set(CMAKE_MODULE_PATH ${PROJECT_SOURCE_DIR}/cmake)

find_package(SndFile REQUIRED)

add_definitions(-DUSE_CPP_DEBUG_LOGGING)
add_definitions(-DNO_EQUALIZATION)

set(CMAKE_OSX_DEPLOYMENT_TARGET "10.10")


add_executable(PnGenerator
               lfsr.c)

target_link_libraries(PnGenerator ${SNDFILE_LIBRARIES})
