# backend/geometry/tests/conftest.py
"""Pytest configuration for geometry tests"""

import os
import sys
import pytest

# Add FreeCAD lib directory to Python path
CONDA_ENV = os.path.join(os.path.expanduser("~"), "miniforge3/envs/eurotempl")
FREECAD_LIB = os.path.join(CONDA_ENV, "lib")
if FREECAD_LIB not in sys.path:
    sys.path.append(FREECAD_LIB)

# Also need to set PYTHONPATH for FreeCAD modules
os.environ["PYTHONPATH"] = FREECAD_LIB

import FreeCAD as App
import Part

@pytest.fixture(scope="function")
def freecad_doc():
    doc = App.newDocument("TestDoc")
    yield doc
    App.closeDocument(doc.Name)

@pytest.fixture(scope="session")
def cgal_converter():
    from geometry.core.cpp_extensions import cgal_converter
    return cgal_converter.CGALConverter()

@pytest.fixture(scope="session")
def cgal_parametric():
    from geometry.core.cpp_extensions import cgal_parametric
    return cgal_parametric.ParametricShape()