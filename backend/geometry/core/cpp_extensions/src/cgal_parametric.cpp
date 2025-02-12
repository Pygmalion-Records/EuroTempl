#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <CGAL/Simple_cartesian.h>
#include <CGAL/Nef_polyhedron_3.h>
#include <CGAL/Polyhedron_3.h>
#include <CGAL/Polyhedron_incremental_builder_3.h>
#include <vector>

namespace py = pybind11;

typedef CGAL::Simple_cartesian<double> Kernel;
typedef Kernel::Point_3 Point;
typedef CGAL::Polyhedron_3<Kernel> Polyhedron;
typedef CGAL::Nef_polyhedron_3<Kernel> Nef_polyhedron;
typedef Polyhedron::HalfedgeDS HalfedgeDS;

// Builder class for creating polyhedron
template<class HDS>
class Polyhedron_Builder : public CGAL::Modifier_base<HDS> {
public:
    std::vector<std::vector<double>> vertices;
    std::vector<std::vector<int>> faces;

    Polyhedron_Builder(const std::vector<std::vector<double>>& v, 
                      const std::vector<std::vector<int>>& f) 
        : vertices(v), faces(f) {}

    void operator()(HDS& hds) {
        CGAL::Polyhedron_incremental_builder_3<HDS> builder(hds, true);
        builder.begin_surface(vertices.size(), faces.size());

        // Add vertices
        for (const auto& v : vertices) {
            builder.add_vertex(Point(v[0], v[1], v[2]));
        }

        // Add faces
        for (const auto& f : faces) {
            builder.begin_facet();
            for (int idx : f) {
                builder.add_vertex_to_facet(idx);
            }
            builder.end_facet();
        }

        builder.end_surface();
    }
};

class ParametricShape {
private:
    Nef_polyhedron nef;

public:
    ParametricShape() : nef() {}

    void create_from_mesh(const std::vector<std::vector<double>>& vertices,
                         const std::vector<std::vector<int>>& faces) {
        Polyhedron P;
        Polyhedron_Builder<HalfedgeDS> builder(vertices, faces);
        P.delegate(builder);
        nef = Nef_polyhedron(P);
    }

    std::tuple<std::vector<std::vector<double>>, std::vector<std::vector<int>>>
    to_mesh() const {
        Polyhedron P;
        nef.convert_to_polyhedron(P);

        std::vector<std::vector<double>> vertices;
        std::vector<std::vector<int>> faces;
        std::map<Polyhedron::Vertex_const_handle, int> vertex_indices;

        // Extract vertices
        int idx = 0;
        for (auto v = P.vertices_begin(); v != P.vertices_end(); ++v) {
            vertices.push_back({v->point().x(), v->point().y(), v->point().z()});
            vertex_indices[v] = idx++;
        }

        // Extract faces
        for (auto f = P.facets_begin(); f != P.facets_end(); ++f) {
            std::vector<int> face;
            auto h = f->halfedge();
            do {
                face.push_back(vertex_indices[h->vertex()]);
                h = h->next();
            } while (h != f->halfedge());
            faces.push_back(face);
        }

        return std::make_tuple(vertices, faces);
    }

    void boolean_union(const ParametricShape& other) {
        nef += other.nef;
    }

    void boolean_intersection(const ParametricShape& other) {
        nef *= other.nef;
    }

    void boolean_difference(const ParametricShape& other) {
        nef -= other.nef;
    }
};

PYBIND11_MODULE(cgal_parametric, m) {
    m.doc() = "CGAL parametric geometry module";

    py::class_<ParametricShape>(m, "ParametricShape")
        .def(py::init<>())
        .def("create_from_mesh", &ParametricShape::create_from_mesh)
        .def("to_mesh", &ParametricShape::to_mesh)
        .def("boolean_union", &ParametricShape::boolean_union)
        .def("boolean_intersection", &ParametricShape::boolean_intersection)
        .def("boolean_difference", &ParametricShape::boolean_difference);
}
