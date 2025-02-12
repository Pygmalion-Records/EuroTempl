#!/bin/bash
set -e

# Get conda environment path more reliably
CONDA_ENV=$(dirname $(dirname $(which python)))

# Print debug info
echo "Using Conda env: ${CONDA_ENV}"
echo "Python location: $(which python)"

# Create build directory
rm -rf build
mkdir -p build
cd build

# Configure CMake with more explicit Python settings
cmake ../core/cpp_extensions \
    -DCMAKE_BUILD_TYPE=Release \
    -DPython_ROOT_DIR="${CONDA_ENV}" \
    -DPython_EXECUTABLE="$(which python)" \
    -DPYTHON_EXECUTABLE="$(which python)" \
    -DPYTHON_INCLUDE_DIR="${CONDA_ENV}/include/python3.10" \
    -DPYTHON_LIBRARY="${CONDA_ENV}/lib/libpython3.10.dylib" \
    -DPython_INCLUDE_DIRS="${CONDA_ENV}/include/python3.10" \
    -DPython_LIBRARIES="${CONDA_ENV}/lib/libpython3.10.dylib" \
    -DBOOST_ROOT="${CONDA_ENV}" \
    -DBOOST_INCLUDEDIR="${CONDA_ENV}/include" \
    -DBOOST_LIBRARYDIR="${CONDA_ENV}/lib" \
    -DBoost_NO_SYSTEM_PATHS=ON

# Build
cmake --build . -- -j4

# Copy the built libraries to the correct location
mkdir -p ../core/cpp_extensions/lib
cp *.so ../core/cpp_extensions/lib/

cd ..