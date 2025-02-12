cmake_minimum_required(VERSION 3.15)
project(eurotempl_core)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_POSITION_INDEPENDENT_CODE ON)

# Find Python and pybind11
find_package(Python COMPONENTS Interpreter Development REQUIRED)
find_package(pybind11 CONFIG REQUIRED)

# Include directories
include_directories(${CMAKE_CURRENT_SOURCE_DIR}/include)

# Add source files
add_library(geometry_converter STATIC
    src/geometry_converter.cpp
)

# Add the bindings subdirectory
add_subdirectory(bindings)

# Link geometry_converter to the Python module
target_link_libraries(eurotempl_core PRIVATE geometry_converter)