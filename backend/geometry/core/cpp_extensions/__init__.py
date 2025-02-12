import os
import sys

# Get the directory containing this __init__.py file
_current_dir = os.path.dirname(os.path.abspath(__file__))
_lib_dir = os.path.join(_current_dir, 'lib')

# Add the lib directory to Python's path
if _lib_dir not in sys.path:
    sys.path.append(_lib_dir)

# Import the modules directly
import cgal_parametric
import cgal_converter

# Make everything available at the package level
__all__ = ['cgal_parametric', 'cgal_converter']
