cmake_minimum_required(VERSION 3.15)
project(parameters_engine)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_POSITION_INDEPENDENT_CODE ON)

# Find required packages
find_package(Boost REQUIRED COMPONENTS graph thread)
find_package(pybind11 CONFIG REQUIRED)

# Include directories
include_directories(${CMAKE_CURRENT_SOURCE_DIR}/include)
include_directories(${Boost_INCLUDE_DIRS})

# Add library target
add_library(parameters_engine_lib STATIC
    src/parameter_graph.cpp
)

# Link against Boost
target_link_libraries(parameters_engine_lib PRIVATE
    Boost::graph
    Boost::thread
)

# Add Python bindings
add_subdirectory(bindings)