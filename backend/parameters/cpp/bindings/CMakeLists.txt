pybind11_add_module(parameters_engine_ext parameter_bindings.cpp)

target_include_directories(parameters_engine_ext PRIVATE
    ${CMAKE_CURRENT_SOURCE_DIR}/../include
)

target_link_libraries(parameters_engine_ext PRIVATE
    parameters_engine_lib
    ${Boost_LIBRARIES}
)

set_target_properties(parameters_engine_ext PROPERTIES
    OUTPUT_NAME "parameters_engine"
)