cmake_minimum_required (VERSION 2.8) 

project(CppHmmLibrary)

ADD_DEFINITIONS(
-std=c++11
)

if (${CMAKE_SYSTEM_NAME} MATCHES "Linux")
ADD_DEFINITIONS(
-DLINUX
)
MESSAGE(STATUS "LINUX")
endif()


set(CMAKE_MODULE_PATH ${PROJECT_SOURCE_DIR}/../cmake)
set("CMAKE_CXX_FLAGS" "${CMAKE_CXX_FLAGS} -Wall -Werror -std=c++11 -Wc++11-extensions")

add_definitions(-DUSE_CPP_DEBUG_LOGGING)

FIND_PACKAGE(GSL REQUIRED)
include_directories("${GSL_INCLUDE_DIR}")

include_directories ("${PROJECT_SOURCE_DIR}")


#compile our alg code
add_library(cpphmm STATIC
InitialModelGenerator.cpp
HiddenMarkovModel.cpp
AllModels.cpp
CompositeModel.cpp
ReestimationResult.cpp
SerializationHelpers.cpp
MatrixHelpers.cpp
RandomHelpers.cpp
MultiObsSequenceHiddenMarkovModel.cpp
HmmHelpers.cpp
MultiObsSequence.cpp
Ensemble.cpp
)

target_link_libraries(cpphmm pthread ${GSL_LIBRARIES})
