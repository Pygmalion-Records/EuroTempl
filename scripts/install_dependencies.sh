#!/bin/bash

# Install OCCT and build dependencies
brew install opencascade
brew install cmake swig

# activate conda environment and install dependencies
conda env create -f environment.yml
conda activate EuroTempl