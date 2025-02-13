"""EuroTempl System
Copyright (c) 2024 Pygmalion Records"""

from typing import Optional
from django.contrib.gis.geos import GEOSGeometry, Point, MultiPoint


class GEOSConverter:
    @staticmethod
    def to_geos(shape) -> Optional[GEOSGeometry]:
        """Convert the CAD model to a GEOS geometry."""
        if not self.shape:
            return None
        return self.shape_to_geos(self.shape)
        
    @staticmethod
    def from_geos(geom) -> Optional[object]:
        """Create a CAD model from a GEOS geometry."""
        try:
            cgal_shape = geos_to_cgal(geom)
            self.shape = cgal_to_freecad(cgal_shape)
            if self.shape:
                obj = self.doc.addObject("Part::Feature", "Shape")
                obj.Shape = self.shape
                self.doc.recompute()
        except Exception as e:
            print(f"Error creating shape: {e}")
            self.shape = None



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