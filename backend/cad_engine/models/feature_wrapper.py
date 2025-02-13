"""EuroTempl System
Copyright (c) 2024 Pygmalion Records"""

from django.contrib.gis.db import models
import FreeCAD as App
import FreeCADGui as Gui
from FreeCAD import Units, Vector
from typing import Dict, Any, Optional, Tuple
import uuid
from dataclasses import dataclass
from django.core.exceptions import ValidationError

class FeatureWrapper:
    """Wrapper for FreeCAD features providing grid functionality."""
    
    def __init__(self, doc, grid_config=None):
        """Initialize wrapper with FreeCAD document."""
        self.doc = doc
        self.grid_size = 25.0  # Default grid size in mm
        self.tolerance = 1e-6  # Grid alignment tolerance
        
        # Sync with grid config if provided
        if grid_config:
            self.grid_size = grid_config.size
            self.tolerance = grid_config.tolerance
        
    def _setup_properties(self, obj):
        """Set up FreeCAD properties with proper types and metadata."""
        try:
            # Add standard properties
            obj.addProperty("App::PropertyString", "Name", "Base", "Feature name")
            obj.addProperty("App::PropertyString", "Type", "Base", "Feature type")
            obj.addProperty("App::PropertyUUID", "UniqueId", "Base", "Unique identifier")
            obj.setEditorMode("UniqueId", 1)  # Read-only
            
            # Add grid alignment properties
            obj.addProperty("App::PropertyBool", "GridAligned", "Grid", "Grid alignment status")
            obj.addProperty("App::PropertyFloat", "GridDeviation", "Grid", "Grid alignment deviation")
            
            # Set initial values
            obj.UniqueId = str(uuid.uuid4())
            obj.GridAligned = True
            
        except Exception as e:
            App.Console.PrintError(f"Error setting up properties: {str(e)}\n")
            raise
            
    def execute(self, obj):
        """Execute when the object is recomputed."""
        try:
            if obj.GridAligned and hasattr(obj, "Shape"):
                self._ensure_grid_alignment(obj)
        except Exception as e:
            App.Console.PrintError(f"Error during execution: {str(e)}\n")
            raise
            
    def _ensure_grid_alignment(self, obj):
        """Ensure object is aligned to grid."""
        if not hasattr(obj, "Shape") or not obj.Shape or not hasattr(obj.Shape, "Vertexes"):
            return
            
        # Add grid properties if needed
        if not hasattr(obj, "GridAligned"):
            obj.addProperty("App::PropertyBool", "GridAligned", "Grid", "Grid alignment state")
        if not hasattr(obj, "GridDeviation"):
            obj.addProperty("App::PropertyFloat", "GridDeviation", "Grid", "Grid deviation value")
        
        obj.GridAligned = True
        obj.GridDeviation = 0.0
    
        # Check grid alignment
        for v in obj.Shape.Vertexes:
            # Calculate aligned coordinates
            aligned_x = round(v.X / self.grid_size) * self.grid_size
            aligned_y = round(v.Y / self.grid_size) * self.grid_size
            
            # Calculate deviation
            dx = abs(v.X - aligned_x)
            dy = abs(v.Y - aligned_y)
            deviation = max(dx, dy)
            obj.GridDeviation = max(obj.GridDeviation, deviation)
            
            if deviation > self.tolerance:
                obj.GridAligned = False
                break