// EuroTempl Parameters Engine
// Copyright (c) 2024 Pygmalion Records

#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include "parameter_graph.hpp"

namespace py = pybind11;

PYBIND11_MODULE(parameters_engine, m) {
    m.doc() = "EuroTempl parameter management module";

    py::class_<eurotempl::parameters::ParameterGraphManager>(m, "ParameterGraphManager")
        .def(py::init<>())
        .def("add_parameter", &eurotempl::parameters::ParameterGraphManager::addParameter,
            py::arg("id"), py::arg("name"), py::arg("type"), py::arg("value"),
            "Add a new parameter to the graph")
        .def("add_dependency", &eurotempl::parameters::ParameterGraphManager::addDependency,
            py::arg("from_id"), py::arg("to_id"), py::arg("relationship"),
            "Add a dependency between parameters")
        .def("get_affected_parameters", 
            &eurotempl::parameters::ParameterGraphManager::getAffectedParameters,
            py::arg("changed_id"),
            "Get parameters affected by a change");
}