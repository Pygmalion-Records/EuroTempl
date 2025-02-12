"""EuroTempl System
Copyright (c) 2024 Pygmalion Records"""

import os
import sys
import pytest
from django.contrib.gis.geos import Point, GEOSGeometry
from cad_engine.conversion import geos_to_freecad, freecad_to_geos

# Add FreeCAD lib directory to Python path
CONDA_ENV = os.path.join(os.path.expanduser("~"), "miniforge3/envs/eurotempl")
FREECAD_LIB = os.path.join(CONDA_ENV, "lib")
if FREECAD_LIB not in sys.path:
    sys.path.append(FREECAD_LIB)

# Also need to set PYTHONPATH for FreeCAD modules
os.environ["PYTHONPATH"] = FREECAD_LIB

import FreeCAD as App
import Part

@pytest.mark.django_db
def test_freecad_geos_conversion():
    # Create a new empty document
    doc = App.newDocument()
    
    # Test geos_to_freecad
    x, y, z = 25, 25, 25
    original_point = Point(x, y, z, srid=4326)
    freecad_vector = geos_to_freecad(original_point)
    
    assert isinstance(freecad_vector, App.Vector)
    assert freecad_vector.x == x
    assert freecad_vector.y == y
    assert freecad_vector.z == z

    # Test freecad_to_geos
    freecad_shape = Part.makeBox(10, 10, 10)
    geos_geom = freecad_to_geos(freecad_shape)

    assert isinstance(geos_geom, GEOSGeometry)
    assert geos_geom.geom_type == 'MultiPoint'
    assert len(geos_geom) == 8  # A box has 8 vertices
    for point in geos_geom:
        assert 0 <= point.x <= 10
        assert 0 <= point.y <= 10
        assert 0 <= point.z <= 10
    
    # Cleanup
    App.closeDocument(doc.Name)