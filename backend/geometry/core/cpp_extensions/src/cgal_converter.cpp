#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <CGAL/Simple_cartesian.h>
#include <CGAL/Surface_mesh.h>
#include <CGAL/Polygon_mesh_processing/triangulate_faces.h>
#include <CGAL/Polygon_mesh_processing/compute_normal.h>
#include <vector>
#include <map>

namespace py = pybind11;

typedef CGAL::Simple_cartesian<double> Kernel;
typedef Kernel::Point_3 Point_3;
typedef CGAL::Surface_mesh<Point_3> Mesh;
typedef Kernel::Vector_3 Vector_3;

std::tuple<std::vector<std::vector<double>>, std::vector<std::vector<int>>>
create_and_return_mesh(const std::vector<std::vector<double>>& vertices,
                      const std::vector<std::vector<int>>& faces) {
    Mesh mesh;
    std::vector<Mesh::Vertex_index> vertex_handles;
    
    // Add vertices
    for (const auto& v : vertices) {
        vertex_handles.push_back(mesh.add_vertex(Point_3(v[0], v[1], v[2])));
    }
    
    // Add faces
    for (const auto& face : faces) {
        std::vector<Mesh::Vertex_index> face_vertices;
        for (int idx : face) {
            face_vertices.push_back(vertex_handles[idx]);
        }
        mesh.add_face(face_vertices);
    }
    
    // Convert back to arrays
    std::vector<std::vector<double>> out_vertices;
    std::vector<std::vector<int>> out_faces;
    
    for (Mesh::Vertex_index v : mesh.vertices()) {
        const auto& point = mesh.point(v);
        out_vertices.push_back({point.x(), point.y(), point.z()});
    }
    
    for (Mesh::Face_index f : mesh.faces()) {
        std::vector<int> face;
        CGAL::Vertex_around_face_circulator<Mesh> vcirc(mesh.halfedge(f), mesh);
        CGAL::Vertex_around_face_circulator<Mesh> vend = vcirc;
        do {
            face.push_back((int)*vcirc);
            ++vcirc;
        } while (vcirc != vend);
        out_faces.push_back(face);
    }
    
    return std::make_tuple(out_vertices, out_faces);
}

std::vector<std::vector<int>> triangulate_mesh(const std::vector<std::vector<double>>& vertices,
                                             const std::vector<std::vector<int>>& faces) {
    auto [v, f] = create_and_return_mesh(vertices, faces);
    return f;  // Already triangulated by CGAL
}

std::vector<std::vector<double>> compute_normals(const std::vector<std::vector<double>>& vertices,
                                               const std::vector<std::vector<int>>& faces) {
    Mesh mesh;
    auto [v, f] = create_and_return_mesh(vertices, faces);
    std::vector<std::vector<double>> normals;
    
    for (Mesh::Face_index face : mesh.faces()) {
        Vector_3 normal = CGAL::Polygon_mesh_processing::compute_face_normal(face, mesh);
        normals.push_back({normal.x(), normal.y(), normal.z()});
    }
    
    return normals;
}

PYBIND11_MODULE(cgal_converter, m) {
    m.doc() = "CGAL mesh conversion utilities";
    m.def("create_mesh", &create_and_return_mesh, "Create a CGAL mesh from vertices and faces");
    m.def("triangulate_faces", &triangulate_mesh, "Triangulate mesh faces");
    m.def("compute_face_normals", &compute_normals, "Compute face normals");
}
