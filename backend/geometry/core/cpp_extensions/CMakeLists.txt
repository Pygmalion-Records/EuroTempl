cmake_minimum_required(VERSION 3.15)
project(geometry_extensions)

# Set CMake policies
if(POLICY CMP0074)
    cmake_policy(SET CMP0074 NEW)
endif()
if(POLICY CMP0144)
    cmake_policy(SET CMP0144 NEW)
endif()
if(POLICY CMP0148)
    cmake_policy(SET CMP0148 NEW)
endif()
if(POLICY CMP0167)
    cmake_policy(SET CMP0167 NEW)
endif()

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_POSITION_INDEPENDENT_CODE ON)

# Find Python first
find_package(Python 3.6 REQUIRED COMPONENTS Interpreter Development)

# Get Python prefix path
execute_process(
    COMMAND "${Python_EXECUTABLE}" -c "import sys; print(sys.prefix)"
    OUTPUT_VARIABLE PYTHON_PREFIX
    OUTPUT_STRIP_TRAILING_WHITESPACE
)

# Set paths relative to conda environment
set(CMAKE_PREFIX_PATH ${PYTHON_PREFIX})
set(BOOST_ROOT ${PYTHON_PREFIX})
set(CGAL_DIR ${PYTHON_PREFIX})
set(GMP_ROOT_DIR ${PYTHON_PREFIX})
set(MPFR_ROOT_DIR ${PYTHON_PREFIX})

# Find required packages
find_package(pybind11 REQUIRED)
find_package(Boost 1.66 REQUIRED)
find_package(CGAL REQUIRED COMPONENTS Core)
find_package(GMP REQUIRED)
find_package(MPFR REQUIRED)

# Include directories
include_directories(${Boost_INCLUDE_DIRS})
include_directories(${CGAL_INCLUDE_DIRS})
include_directories(${Python_INCLUDE_DIRS})
include_directories(${GMP_INCLUDE_DIRS})
include_directories(${MPFR_INCLUDE_DIRS})

# Set source files
set(CONVERTER_SOURCES
    src/cgal_converter.cpp
)

set(PARAMETRIC_SOURCES
    src/cgal_parametric.cpp
)

# Create the extension modules
pybind11_add_module(cgal_converter ${CONVERTER_SOURCES})
pybind11_add_module(cgal_parametric ${PARAMETRIC_SOURCES})

# Link against required libraries
target_link_libraries(cgal_converter PRIVATE CGAL::CGAL CGAL::CGAL_Core)
target_link_libraries(cgal_parametric PRIVATE CGAL::CGAL CGAL::CGAL_Core)

# Set output directory
set_target_properties(cgal_converter PROPERTIES
    LIBRARY_OUTPUT_DIRECTORY "${CMAKE_CURRENT_SOURCE_DIR}/lib"
)
set_target_properties(cgal_parametric PROPERTIES
    LIBRARY_OUTPUT_DIRECTORY "${CMAKE_CURRENT_SOURCE_DIR}/lib"
)

# Debug output
message(STATUS "Python_EXECUTABLE: ${Python_EXECUTABLE}")
message(STATUS "PYTHON_PREFIX: ${PYTHON_PREFIX}")
message(STATUS "CMAKE_PREFIX_PATH: ${CMAKE_PREFIX_PATH}")
message(STATUS "CGAL_DIR: ${CGAL_DIR}")
