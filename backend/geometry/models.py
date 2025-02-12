from django.contrib.gis.db import models

class GeometryStore(models.Model):
    """Model to store geometries in PostGIS"""
    geometry = models.GeometryField(srid=4326, dim=3)  # Add dim=3 for 3D support
    metadata = models.JSONField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = 'geometry'