cmake_minimum_required (VERSION 2.8) 

PROJECT (HmmTrainer)

set(CMAKE_INCLUDE_PATH ${PROJECT_SOURCE_DIR}/)
set(CMAKE_MODULE_PATH ${PROJECT_SOURCE_DIR}/../cmake)

include_directories("../src/")


#compile algs
add_subdirectory("../src/" "${CMAKE_CURRENT_BINARY_DIR}/main")


add_executable(trainer
               main.cpp
               trainer.cpp
               hmmfactory.cpp)

target_link_libraries(trainer cpphmm )

