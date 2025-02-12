// EuroTempl System
// Copyright (c) 2024 Pygmalion Records

#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include "geometry_converter.hpp"

namespace py = pybind11;

PYBIND11_MODULE(eurotempl_core, m) {
    m.doc() = "EuroTempl geometry conversion module";

    py::class_<eurotempl::GeometryConverter>(m, "GeometryConverter")
        .def_static("align_to_grid", &eurotempl::GeometryConverter::alignToGrid,
            py::arg("points"), py::arg("grid_size") = 25.0,
            "Align points to the EuroTempl grid system")
        .def_static("validate_grid_alignment", &eurotempl::GeometryConverter::validateGridAlignment,
            py::arg("points"), py::arg("grid_size") = 25.0,
            "Validate if points are aligned to the grid")
        .def_static("to_geos", &eurotempl::GeometryConverter::toGeos,
            "Convert coordinates to GEOS format")
        .def_static("from_geos", &eurotempl::GeometryConverter::fromGeos,
            "Convert coordinates from GEOS format");
}