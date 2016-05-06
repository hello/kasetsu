cmake_minimum_required (VERSION 2.8)

PROJECT (PnGenerator)

set(CMAKE_INCLUDE_PATH ${PROJECT_SOURCE_DIR}/)
set(CMAKE_MODULE_PATH ${PROJECT_SOURCE_DIR}/cmake)

find_package(SndFile REQUIRED)

include_directories (${SNDFILE_INCLUDE_DIRS})


set(CMAKE_OSX_DEPLOYMENT_TARGET "10.10")


add_executable(PnGenerator
               main.cpp
               pn.c
               upconvert.c)

target_link_libraries(PnGenerator ${SNDFILE_LIBRARIES})
