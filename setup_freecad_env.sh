#!/bin/bash

# FreeCAD paths
export FREECAD_PATH="/Applications/FreeCAD.app/Contents"
export PYTHONPATH="${FREECAD_PATH}/Resources/lib/python3.11/site-packages:${FREECAD_PATH}/Resources/Mod:${PYTHONPATH}"
export DYLD_FRAMEWORK_PATH="${FREECAD_PATH}/Frameworks:${FREECAD_PATH}/MacOS"
export DYLD_LIBRARY_PATH="${FREECAD_PATH}/Resources/lib:${DYLD_LIBRARY_PATH}"
export PATH_TO_FREECAD_LIBDIR="${FREECAD_PATH}/Resources/lib"

# Run the command passed as arguments
exec "$@"
