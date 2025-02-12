from .conversion_algorithms import create_mesh_from_arrays

class ParametricShape:
    def __init__(self):
        self.vertices = None
        self.faces = None

    def create_from_mesh(self, vertices, faces):
        """Create a parametric shape from mesh data."""
        self.vertices, self.faces = create_mesh_from_arrays(vertices, faces)

    def boolean_union(self, other):
        """Perform boolean union with another shape."""
        if self.vertices is None or other.vertices is None:
            return
        
        # Combine vertices from both shapes
        offset = len(self.vertices)
        new_vertices = self.vertices + other.vertices
        
        # Adjust face indices for the second shape
        new_faces = self.faces + [[idx + offset for idx in face] for face in other.faces]
        
        # Update the current shape
        self.vertices = new_vertices
        self.faces = new_faces

    def to_mesh(self):
        """Convert the shape to mesh representation."""
        if self.vertices is None:
            return [], []
        return self.vertices, self.faces