from django.contrib.gis.db import models
from django.contrib.gis.geos import GEOSGeometry
from django.contrib.gis.db.models import Collect
from .cad_model import CADModel
from .models import GeometryStore

class SpatialManager:
    @staticmethod
    def store_geometry(geom: GEOSGeometry, metadata: dict = None):
        """Store geometry in PostGIS"""
        try:
            store = GeometryStore.objects.create(
                geometry=geom,
                metadata=metadata
            )
            return store.id
        except Exception as e:
            print(f"Error storing geometry: {e}")
            return None

    @staticmethod
    def query_by_bounds(bounds):
        """Query geometries within given bounds"""
        try:
            return GeometryStore.objects.filter(
                geometry__intersects=bounds
            ).values_list('geometry', flat=True)
        except Exception as e:
            print(f"Error querying geometries: {e}")
            return None

    @staticmethod
    def convert_to_cad(geom: GEOSGeometry):
        """Convert PostGIS geometry to CAD format"""
        try:
            model = CADModel("converted_geometry")
            model.create_from_geos(geom)
            return model
        except Exception as e:
            print(f"Error converting to CAD: {e}")
            return None