cmake_minimum_required(VERSION 3.15)
project(parameters_engine)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_POSITION_INDEPENDENT_CODE ON)

# Find required packages
find_package(Boost REQUIRED COMPONENTS graph thread)
find_package(pybind11 CONFIG REQUIRED)

# Add the cpp subdirectory
add_subdirectory(cpp)