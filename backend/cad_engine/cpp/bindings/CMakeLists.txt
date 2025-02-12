pybind11_add_module(eurotempl_core geometry_bindings.cpp)

target_include_directories(eurotempl_core PRIVATE
    ${CMAKE_CURRENT_SOURCE_DIR}/../include
)

target_link_libraries(eurotempl_core PRIVATE
    geometry_converter
)

target_compile_options(eurotempl_core PRIVATE
    -Wall
    -Wextra
    -O3
)