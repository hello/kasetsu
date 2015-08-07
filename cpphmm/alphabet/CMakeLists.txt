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


FIND_PACKAGE(JsonCpp REQUIRED)

include_directories("../src/")
include_directories(${JSONCPP_INCLUDE_DIRS})




#compile algs
add_subdirectory("../src/" "${CMAKE_CURRENT_BINARY_DIR}/main")


add_executable(alphabet
               main.cpp)

target_link_libraries(alphabet cpphmm jsoncpp)

