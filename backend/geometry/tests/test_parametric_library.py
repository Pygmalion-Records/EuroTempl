import pytest
from geometry.parametric_library import ParametricShape
from geometry.tests.test_data import CUBE_VERTICES, CUBE_FACES

def test_create_parametric_shape():
    shape = ParametricShape()
    shape.create_from_mesh(CUBE_VERTICES, CUBE_FACES)
    vertices, faces = shape.to_mesh()
    assert len(vertices) == len(CUBE_VERTICES)
    assert len(faces) == len(CUBE_FACES)

def test_boolean_operations():
    shape1 = ParametricShape()
    shape1.create_from_mesh(CUBE_VERTICES, CUBE_FACES)
    
    shape2 = ParametricShape()
    # Create a shifted cube
    shifted_vertices = [[x + 0.5, y + 0.5, z + 0.5] for x, y, z in CUBE_VERTICES]
    shape2.create_from_mesh(shifted_vertices, CUBE_FACES)
    
    # Test union
    shape1.boolean_union(shape2)
    vertices, faces = shape1.to_mesh()
    assert len(vertices) > len(CUBE_VERTICES)
    assert len(faces) > len(CUBE_FACES)
