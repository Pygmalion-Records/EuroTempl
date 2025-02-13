# cad_engine/cad_model.py

import FreeCAD as App
from ..utils.gui_helper import initialize_gui
Gui = initialize_gui(headless=True)  # Force headless mode for now
from FreeCAD import Units, Vector
from typing import Dict, Any, Optional, Tuple
import uuid
from dataclasses import dataclass
from django.core.exceptions import ValidationError
from .grid_config import GridConfig
from .feature_wrapper import FeatureWrapper
from django.contrib.gis.geos import GEOSGeometry, Point, MultiPoint, Polygon
from ..converters.geos_converter import geos_to_freecad, freecad_to_geos
import Part


class CADModel:
    """Enhanced CAD Model Manager for FreeCAD integration."""
    
    def __init__(self, name: str):
        """Initialize CAD model with proper error handling and setup."""
        try:
            # Create document with unique name
            self.name = name
            self.doc_name = f"{name}_{uuid.uuid4().hex[:8]}"
            self.doc = App.newDocument(self.doc_name)
            
            # Initialize configuration
            self.grid_config = GridConfig()
            self.features = {}  # Map UUID to feature
            
            # Set up document
            self._setup_document()
            self._setup_grid()
            
            # Initialize wrapper with grid config directly
            self.wrapper = FeatureWrapper(self.doc, self.grid_config)
            
        except Exception as e:
            App.Console.PrintError(f"Failed to initialize CAD model: {str(e)}\n")
            raise
            
    def _setup_document(self):
        """Set up the FreeCAD document."""
        try:
            import FreeCAD as App
            self.doc = App.newDocument(self.name)
            # Set units through FreeCAD parameters
            params = App.ParamGet("User parameter:BaseApp/Preferences/Units")
            params.SetInt("UserSchema", 0)  # 0 = Standard (mm/kg/s/degree)
        except ImportError:
            raise ImportError("FreeCAD is required for CAD operations")
            
    def _setup_grid(self):
        """Configure grid system using FreeCAD preferences."""
        try:
            import FreeCAD as App
            params = App.ParamGet("User parameter:BaseApp/Preferences/Mod")
    
            # Set grid parameters
            params.SetFloat("GridSize", self.grid_config.size)
            params.SetBool("GridSnap", self.grid_config.snap_enabled)
            params.SetString("GridStyle", self.grid_config.style)
    
            # Try to apply to GUI document if available
            try:
                import FreeCADGui as Gui
                # Check if we're in a GUI environment with proper initialization
                if hasattr(Gui, 'ActiveDocument') and Gui.ActiveDocument:
                    Gui.ActiveDocument.ActiveView.setGridSize(self.grid_config.size)
                    Gui.ActiveDocument.ActiveView.setGridSnap(self.grid_config.snap_enabled)
            except (ImportError, AttributeError):
                # GUI is not available or not properly initialized, which is fine for headless operation
                pass
    
        except ImportError:
            raise ImportError("FreeCAD is required for CAD operations")
            
    def create_feature(self, feature_type: str, params: Dict[str, Any] = None) -> Optional[str]:
        """Create a new CAD feature."""
        try:
            # Create feature with unique name
            name = f"{feature_type}_{uuid.uuid4().hex[:8]}"
            
            if feature_type == "Box":
                length = float(params.get("Length", 10.0))
                width = float(params.get("Width", 10.0))
                height = float(params.get("Height", 10.0))
                
                # Create box shape
                shape = Part.makeBox(length, width, height)
                obj = self.doc.addObject("Part::Feature", name)
                obj.Shape = shape
                
            else:
                obj = self.doc.addObject("Part::Feature", name)
            
            # Add grid properties
            self.wrapper._setup_properties(obj)
            self.wrapper._ensure_grid_alignment(obj)
            
            # Store feature ID mapping
            feature_id = str(uuid.uuid4())
            self.features[feature_id] = obj
            
            self.doc.recompute()
            return feature_id
            
        except Exception as e:
            print(f"Error creating feature: {e}")
            return None
            
    def _validate_feature_type(self, feature_type: str) -> bool:
        """Validate if feature type is supported."""
        supported_types = {
            "Box", "Cylinder", "Sphere", "Cone",
            "Torus", "Prism", "Extrusion", "Revolution"
        }
        return feature_type in supported_types
        
    def _apply_parameters(self, obj: object, params: Dict[str, Any]):
        """Apply parameters using FreeCAD's property system."""
        try:
            for name, value in params.items():
                # Validate parameter
                if not self._validate_parameter(name, value):
                    raise ValidationError(f"Invalid parameter: {name} = {value}")
                    
                # Add property if it doesn't exist
                if not hasattr(obj, name):
                    prop_type = self._get_property_type(value)
                    obj.addProperty(prop_type, name, "Parameters", f"Parameter {name}")
                    
                # Set value
                setattr(obj, name, value)
                
        except Exception as e:
            App.Console.PrintError(f"Error applying parameters: {str(e)}\n")
            raise
            
    def _get_property_type(self, value: Any) -> str:
        """Determine appropriate FreeCAD property type."""
        type_map = {
            int: "App::PropertyInteger",
            float: "App::PropertyFloat",
            str: "App::PropertyString",
            bool: "App::PropertyBool",
            Vector: "App::PropertyVector"
        }
        return type_map.get(type(value), "App::PropertyString")
        
    def _validate_parameter(self, name: str, value: Any) -> bool:
        """Validate parameter value."""
        # Add parameter validation logic here
        return True
        
    def get_feature(self, feature_id: str) -> Optional[object]:
        """Get a feature by its ID."""
        try:
            if feature_id not in self.features:
                return None
            return self.features[feature_id]
        except Exception as e:
            print(f"Error getting feature: {e}")
            return None
            
    def save(self, filepath: str):
        """Save document with error handling."""
        try:
            self.doc.saveAs(filepath)
        except Exception as e:
            App.Console.PrintError(f"Error saving document: {str(e)}\n")
            raise
            
    def close(self):
        """Close document with cleanup."""
        try:
            App.closeDocument(self.doc_name)
        except Exception as e:
            App.Console.PrintError(f"Error closing document: {str(e)}\n")
            raise
    
    def from_geos(self, geom: GEOSGeometry) -> Optional[str]:
        """Create a CAD feature from a GEOS geometry."""
        if geom is None:
            raise ValidationError("Failed to convert GEOS geometry")
    
        try:
            if isinstance(geom, Point):
                vector = App.Vector(float(geom.x), float(geom.y), 0.0)
                shape = Part.Vertex(vector)
                
            elif isinstance(geom, Polygon):
                # Get coordinates without closure point
                coords = list(geom.coords[0][:-1])  # Exclude last point (closure)
                points = []
                
                # Create vectors and ensure closure
                for coord in coords:
                    points.append(App.Vector(float(coord[0]), float(coord[1]), 0.0))
                # Explicitly add first point again to close
                points.append(points[0])
                
                # Create wire and face
                wire = Part.makePolygon(points)
                shape = Part.Face(wire)
                
            else:
                raise ValidationError(f"Unsupported geometry type: {type(geom)}")
    
            # Create feature
            name = f"GEOSShape_{uuid.uuid4().hex[:8]}"
            obj = self.doc.addObject("Part::Feature", name)
            obj.Shape = shape
            
            # Add grid properties
            self.wrapper._setup_properties(obj)
            self.wrapper._ensure_grid_alignment(obj)
            
            # Store feature ID mapping
            feature_id = str(uuid.uuid4())
            self.features[feature_id] = obj
            
            self.doc.recompute()
            return feature_id
    
        except Exception as e:
            print(f"Error creating shape: {e}")
            return None

    def to_geos(self, feature_id: str) -> Optional[GEOSGeometry]:
        """Convert a CAD feature to GEOS geometry."""
        try:
            feature = self.get_feature(feature_id)
            if not feature:
                raise ValidationError(f"Invalid feature ID: {feature_id}")
            if not feature.Shape:
                raise ValidationError("Feature has no shape")
    
            shape_type = feature.Shape.ShapeType
            
            if shape_type == "Vertex":
                p = feature.Shape.Point
                return Point(p.x, p.y)
                
            elif shape_type == "Face":
                vertices = [(v.X, v.Y) for v in feature.Shape.Vertexes]
                if vertices[0] != vertices[-1]:
                    vertices.append(vertices[0])
                return Polygon(vertices)
                
            elif shape_type == "Solid":
                center = feature.Shape.CenterOfMass
                return Point(center.x, center.y)
                
            else:
                raise ValidationError(f"Unsupported shape type: {shape_type}")
    
        except ValidationError:
            raise  # Re-raise ValidationError
        except Exception as e:
            print(f"Error converting to GEOS: {e}")
            return None