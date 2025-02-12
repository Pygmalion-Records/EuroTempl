from django.contrib.gis.geos import GEOSGeometry, Point
from .core.cpp_extensions import cgal_converter
import numpy as np

def create_mesh_from_arrays(vertices, faces):
    """Create a CGAL mesh from vertex and face arrays."""
    # Ensure all inputs are properly formatted
    vertices = np.array(vertices, dtype=float).tolist()
    faces = np.array(faces, dtype=int).tolist()
    return vertices, faces  # Return as tuple for now until CGAL binding is fixed


def extract_mesh_arrays(mesh):
    """Extract vertex and face arrays from mesh data."""
    if isinstance(mesh, tuple) and len(mesh) == 2:
        return mesh
    return [], []


def convert_to_triangles(vertices, faces):
    """Convert a mesh with arbitrary polygonal faces to triangles."""
    triangulated_faces = []
    for face in faces:
        if len(face) == 3:
            triangulated_faces.append(face)
        else:
            # Simple fan triangulation
            for i in range(1, len(face) - 1):
                triangulated_faces.append([face[0], face[i], face[i + 1]])
    return triangulated_faces


def compute_face_normals(vertices, faces):
    """Compute normal vectors for each face in the mesh."""
    normals = []
    vertices = np.array(vertices)
    
    for face in faces:
        if len(face) >= 3:
            v1 = vertices[face[1]] - vertices[face[0]]
            v2 = vertices[face[2]] - vertices[face[0]]
            normal = np.cross(v1, v2)
            norm = np.linalg.norm(normal)
            if norm > 0:
                normal = normal / norm
            normals.append(normal.tolist())
    
    return normals

def geos_to_cgal(geom):
    """Convert GEOS geometry to CGAL."""
    if isinstance(geom, Point):
        return [[geom.x, geom.y, geom.z]], [[0]]
    elif isinstance(geom, GEOSGeometry):
        coords = list(geom.coords)
        if coords:
            if isinstance(coords[0], (tuple, list)):
                vertices = [[x, y, 0] for x, y in coords]
            else:
                vertices = [[coords[0], coords[1], 0]]
            faces = [list(range(len(vertices)))]
            return vertices, faces
    return None

def cgal_to_freecad(cgal_shape):
    """Convert CGAL shape to FreeCAD."""
    try:
        import FreeCAD
        import Part
        
        if cgal_shape is None:
            return None
            
        vertices, faces = cgal_shape
        if not vertices or not faces:
            return None
        
        # Create a compound shape from faces
        compound = []
        for face in faces:
            if len(face) >= 3:
                points = [FreeCAD.Vector(vertices[idx][0], vertices[idx][1], vertices[idx][2]) 
                         for idx in face]
                try:
                    wire = Part.makePolygon(points + [points[0]])  # Close the polygon
                    face = Part.Face(wire)
                    compound.append(face)
                except Part.OCCError:
                    continue
        
        if compound:
            return Part.makeCompound(compound)
            
    except ImportError:
        pass
    
    return None