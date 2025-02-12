"""EuroTempl System
Copyright (c) 2024 Pygmalion Records"""

from setuptools import setup, Extension
from setuptools.command.build_ext import build_ext
import sys
import os
import subprocess
from pathlib import Path
"""
This setup provides:

Grid-aligned geometry conversion between FreeCAD and GEOS formats
High-performance C++ implementation with Python bindings
Proper error handling and type safety
Compliance with EuroTempl's 25mm grid system
Thread-safe operations (noexcept guarantees)
"""
class CMakeExtension(Extension):
    def __init__(self, name, sourcedir=""):
        Extension.__init__(self, name, sources=[])
        self.sourcedir = os.path.abspath(sourcedir)

class CMakeBuild(build_ext):
    def run(self):
        try:
            subprocess.check_output(["cmake", "--version"])
        except OSError:
            raise RuntimeError("CMake must be installed")
        
        for ext in self.extensions:
            self.build_extension(ext)

    def build_extension(self, ext):
        extdir = os.path.abspath(os.path.dirname(self.get_ext_fullpath(ext.name)))
        
        # Create build directory
        build_temp = Path(self.build_temp)
        build_temp.mkdir(parents=True, exist_ok=True)
        
        cmake_args = [
            f"-DCMAKE_LIBRARY_OUTPUT_DIRECTORY={extdir}",
            f"-DPYTHON_EXECUTABLE={sys.executable}",
            "-DCMAKE_BUILD_TYPE=Release"
        ]
        
        build_args = ["--config", "Release"]

        # Point CMake to the cpp directory containing CMakeLists.txt
        cpp_dir = os.path.join(os.path.dirname(__file__), "cpp")
        
        subprocess.check_call(
            ["cmake", cpp_dir] + cmake_args,
            cwd=self.build_temp
        )
        subprocess.check_call(
            ["cmake", "--build", "."] + build_args,
            cwd=self.build_temp
        )

setup(
    name="eurotempl_core",
    ext_modules=[CMakeExtension("eurotempl_core")],
    cmdclass={"build_ext": CMakeBuild},
)