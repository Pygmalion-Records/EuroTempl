"""EuroTempl System
Copyright (c) 2024 Pygmalion Records"""

from django.contrib.gis.geos import Point, MultiPoint

def geos_to_freecad(geos_geom):
    """Convert GEOS geometry to FreeCAD vector."""
    try:
        import FreeCAD as App
    except ImportError:
        raise ImportError("FreeCAD is required for CAD operations")
    return App.Vector(geos_geom.x, geos_geom.y, geos_geom.z)

def freecad_to_geos(freecad_shape):
    """Convert FreeCAD shape to GEOS geometry."""
    try:
        import FreeCAD as App  # noqa: F401
    except ImportError:
        raise ImportError("FreeCAD is required for CAD operations")
    vertices = []
    for vertex in freecad_shape.Vertexes:
        vertices.append(Point(vertex.X, vertex.Y, vertex.Z))
    return MultiPoint(vertices)