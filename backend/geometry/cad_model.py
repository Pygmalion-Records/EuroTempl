import os
import FreeCAD as App
import Part
from django.contrib.gis.geos import GEOSGeometry
from .conversion_algorithms import geos_to_cgal, cgal_to_freecad

class CADModel:
    def __init__(self, name):
        self.name = name
        # Create a temporary directory for test documents if in test mode
        if 'PYTEST_CURRENT_TEST' in os.environ:
            import tempfile
            self.temp_dir = tempfile.mkdtemp()
            # Create an empty document instead of trying to open one
            self.doc = App.newDocument(name)
            self.doc.saveAs(os.path.join(self.temp_dir, name + '.FCStd'))
        else:
            self.doc = App.newDocument(name)
        self.shape = None

    def __del__(self):
        # Cleanup temporary files in test mode
        if hasattr(self, 'temp_dir'):
            import shutil
            try:
                App.closeDocument(self.name)
                shutil.rmtree(self.temp_dir)
            except:
                pass

    def create_from_geos(self, geom):
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

    def modify_parameters(self, params):
        """Modify the model using parametric operations."""
        try:
            if "height" in params and "width" in params:
                box = Part.makeBox(params["width"], params["width"], params["height"])
                self.shape = box
                obj = self.doc.addObject("Part::Feature", "Modified")
                obj.Shape = self.shape
                self.doc.recompute()
        except Exception as e:
            print(f"Error modifying shape: {e}")
            self.shape = None

    def to_geos(self):
        """Convert the CAD model to a GEOS geometry."""
        if not self.shape:
            return None
        return self.shape_to_geos(self.shape)

    @staticmethod
    def shape_to_geos(shape):
        """Convert a FreeCAD shape to GEOS geometry."""
        try:
            bbox = shape.BoundBox
            coords = [
                (bbox.XMin, bbox.YMin),
                (bbox.XMax, bbox.YMin),
                (bbox.XMax, bbox.YMax),
                (bbox.XMin, bbox.YMax),
                (bbox.XMin, bbox.YMin)
            ]
            return GEOSGeometry(f'POLYGON(({",".join([f"{x} {y}" for x, y in coords])}))')
        except:
            return None