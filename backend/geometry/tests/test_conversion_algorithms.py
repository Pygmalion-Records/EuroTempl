import pytest
from geometry.conversion_algorithms import (
    convert_to_triangles,
    compute_face_normals,
    create_mesh_from_arrays,
    extract_mesh_arrays
)
from geometry.tests.test_data import CUBE_VERTICES, CUBE_FACES

def test_mesh_conversion():
    mesh = create_mesh_from_arrays(CUBE_VERTICES, CUBE_FACES)
    vertices, faces = extract_mesh_arrays(mesh)
    assert len(vertices) == len(CUBE_VERTICES)
    assert len(faces) == len(CUBE_FACES)

def test_triangulation():
    triangles = convert_to_triangles(CUBE_VERTICES, CUBE_FACES)
    assert all(len(face) == 3 for face in triangles)
    assert len(triangles) > len(CUBE_FACES)

def test_face_normals():
    normals = compute_face_normals(CUBE_VERTICES, CUBE_FACES)
    assert len(normals) == len(CUBE_FACES)
    assert all(len(normal) == 3 for normal in normals)
