"""CAD kernel initialization and configuration for EuroTempl."""
from OCC.Core.BRepAlgoAPI import BRepAlgoAPI_Fuse, BRepAlgoAPI_Cut
from OCC.Core.BRepBuilderAPI import BRepBuilderAPI_MakeVertex, BRepBuilderAPI_MakeEdge
from OCC.Core.gp import gp_Pnt, gp_Dir, gp_Ax2
import cadquery as cq

class CADKernel:
    """Manages CAD operations using OCCT/pythonocc."""
    
    @staticmethod
    def init_kernel():
        """Initialize the CAD kernel and verify installation."""
        try:
            # Create a simple test shape to verify OCCT
            point = gp_Pnt(0, 0, 0)
            vertex = BRepBuilderAPI_MakeVertex(point).Vertex()
            return True
        except Exception as e:
            print(f"Failed to initialize CAD kernel: {e}")
            return False

    @staticmethod
    def create_solid(vertices, faces):
        """Create a solid from vertices and faces."""
        try:
            # Use CadQuery for higher-level operations
            result = (cq.Workplane("XY")
                     .polyhedron(vertices, faces))
            return result
        except Exception as e:
            print(f"Failed to create solid: {e}")
            return None

    @staticmethod
    def boolean_union(shape1, shape2):
        """Perform boolean union of two shapes."""
        try:
            fuse = BRepAlgoAPI_Fuse(shape1, shape2)
            return fuse.Shape()
        except Exception as e:
            print(f"Boolean union failed: {e}")
            return None