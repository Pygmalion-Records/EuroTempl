import pytest
from django.contrib.gis.geos import Point, Polygon
from geometry.spatial_data import SpatialManager
from django.db import transaction, connection

@pytest.mark.django_db(transaction=True)
class TestSpatialManager:
    @pytest.fixture(autouse=True)
    def setup_database(self, django_db_setup, django_db_blocker):
        with django_db_blocker.unblock():
            with connection.cursor() as cursor:
                cursor.execute("CREATE EXTENSION IF NOT EXISTS postgis")
                # Drop the table if it exists to ensure clean state
                cursor.execute("DROP TABLE IF EXISTS geometry_geometrystore")
                # Create table with 3D geometry support
                cursor.execute("""
                    CREATE TABLE geometry_geometrystore (
                        id SERIAL PRIMARY KEY,
                        geometry geometry(GeometryZ, 4326),
                        metadata jsonb,
                        created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP
                    )
                """)
            connection.commit()
        
    def test_store_geometry(self):
        point = Point(0, 0, 0, srid=4326)
        metadata = {"name": "test_point"}
        stored_id = SpatialManager.store_geometry(point, metadata)
        assert stored_id is not None

    def test_query_by_bounds(self):
        # Create test data
        point1 = Point(0, 0, 0, srid=4326)
        point2 = Point(1, 1, 1, srid=4326)
        with transaction.atomic():
            SpatialManager.store_geometry(point1)
            SpatialManager.store_geometry(point2)

        bounds = Polygon.from_bbox((-.5, -.5, 0.5, 0.5))
        bounds.srid = 4326
        results = SpatialManager.query_by_bounds(bounds)
        assert len(results) == 1

    def test_convert_to_cad(self):
        point = Point(0, 0, 0, srid=4326)
        cad_obj = SpatialManager.convert_to_cad(point)
        assert cad_obj is not None