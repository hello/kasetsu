cmake_minimum_required (VERSION 2.8)

PROJECT (PnGeneratorStuff)

set(CMAKE_INCLUDE_PATH ${PROJECT_SOURCE_DIR}/)
set(CMAKE_MODULE_PATH ${PROJECT_SOURCE_DIR}/cmake)

find_package(SndFile REQUIRED)

include_directories (${SNDFILE_INCLUDE_DIRS})


set(CMAKE_OSX_DEPLOYMENT_TARGET "10.10")

add_library(pn STATIC pn.c upconvert.c)

add_executable(PnBpsk
               main_bpsk.cpp)

target_link_libraries(PnBpsk pn ${SNDFILE_LIBRARIES})

add_executable(PnWhiteNoise
                main_white_noise.cpp)

target_link_libraries(PnWhiteNoise pn ${SNDFILE_LIBRARIES})
