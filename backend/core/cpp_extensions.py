"""EuroTempl System
Copyright (c) 2024 Pygmalion Records"""

import os
import sys
from pathlib import Path
from typing import List, Tuple
import numpy as np
from django.contrib.gis.geos import GEOSGeometry, Point

# Add compiled extension to Python path
_module_path = Path(__file__).parent
if _module_path.exists():
    sys.path.append(str(_module_path))

try:
    from eurotempl_core import GeometryConverter
except ImportError:
    raise ImportError("Failed to import C++ extensions. Please build the project first.")

def convert_freecad_to_geos(shape) -> GEOSGeometry:
    """Convert FreeCAD shape to GEOS geometry using optimized C++ code.
    
    Args:
        shape: FreeCAD shape object
        
    Returns:
        GEOSGeometry: PostGIS-compatible geometry
    """
    # Extract vertices from FreeCAD shape
    vertices = [(v.X, v.Y, v.Z) for v in shape.Vertexes]
    
    # Convert to grid-aligned coordinates
    aligned = GeometryConverter.align_to_grid(vertices)
    
    # Convert to GEOS format
    geos_coords = GeometryConverter.to_geos(aligned)
    
    # Create WKT string
    wkt = f'MULTIPOINT Z ({", ".join(f"({x} {y} {z})" for x,y,z in geos_coords)})'
    return GEOSGeometry(wkt)

def convert_geos_to_freecad(geos_geom):
    """Convert GEOS geometry to FreeCAD coordinates using optimized C++ code.
    
    Args:
        geos_geom: GEOSGeometry object
        
    Returns:
        List[Tuple[float, float, float]]: Grid-aligned coordinates
    """
    if isinstance(geos_geom, Point):
        coords = [(geos_geom.x, geos_geom.y, geos_geom.z)]
    else:
        coords = list(geos_geom.coords)
    
    # Convert from GEOS format
    freecad_coords = GeometryConverter.from_geos(coords)
    
    # Ensure grid alignment
    return GeometryConverter.align_to_grid(freecad_coords)