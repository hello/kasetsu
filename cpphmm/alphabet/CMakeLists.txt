cmake_minimum_required (VERSION 2.8) 

PROJECT (HmmAlphabetTrainer)

set(CMAKE_INCLUDE_PATH ${PROJECT_SOURCE_DIR}/)
set(CMAKE_MODULE_PATH ${PROJECT_SOURCE_DIR}/../cmake)

if (${CMAKE_SYSTEM_NAME} MATCHES "Linux")
ADD_DEFINITIONS(
-DLINUX
)
MESSAGE(STATUS "LINUX")
endif()

set(CMAKE_LIBRARY_PATH ${CMAKE_LIBRARY_PATH} "/usr/local/lib")
#set(CMAKE_CXX_FLAGS_DEBUG "-g -D_GLIBCXX_DEBUG -O0")
set("CMAKE_CXX_FLAGS" "${CMAKE_CXX_FLAGS}  -Wall -Werror -std=c++11")

#-stdlib=libc++
#${RAPIDJSON_CXX_FLAGS}

FIND_PACKAGE(JsonCpp REQUIRED)
FIND_PACKAGE(RapidJson REQUIRED)
#FIND_PACKAGE(PLplot REQUIRED)

include_directories("../src/")
include_directories(${JSONCPP_INCLUDE_DIRS})
include_directories(${RAPIDJSON_INCLUDE_DIRS})


#compile algs
add_subdirectory("../src/" "${CMAKE_CURRENT_BINARY_DIR}/main")


add_executable(alphabet
               main.cpp
               DataFile.cpp)

target_link_libraries(alphabet cpphmm ${JSONCPP_LIBRARIES})

