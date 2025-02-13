"""EuroTempl System
Copyright (c) 2024 Pygmalion Records"""

import pytest
from django.contrib.gis.geos import Point, Polygon
from django.core.exceptions import ValidationError
from ..models.cad_model import CADModel

@pytest.fixture
def cad_model(freecad_env):
    """Fixture providing a CADModel instance."""
    model = CADModel("test_model")
    yield model
    model.close()

@pytest.fixture
def cad_model():
    """Fixture providing a CADModel instance."""
    model = CADModel("test_model")
    yield model
    model.close()

@pytest.fixture
def sample_point():
    """Fixture providing a sample GEOS Point."""
    return Point(100.0, 200.0, 0.0)

@pytest.fixture
def sample_polygon():
    """Fixture providing a sample GEOS Polygon."""
    coords = ((0.0, 0.0), (100.0, 0.0), (100.0, 100.0), (0.0, 100.0), (0.0, 0.0))
    return Polygon(coords)

class TestCADModelGEOS:
    """Test suite for CADModel GEOS conversion features."""

    def test_from_geos_point(self, cad_model, sample_point):
        """Test converting GEOS Point to CAD feature."""
        # When
        feature_id = cad_model.from_geos(sample_point)

        # Then
        assert feature_id is not None
        feature = cad_model.get_feature(feature_id)
        assert feature is not None
        assert hasattr(feature, "Shape")
        assert abs(feature.Shape.Vertexes[0].X - 100.0) < 1e-6
        assert abs(feature.Shape.Vertexes[0].Y - 200.0) < 1e-6

    def test_from_geos_polygon(self, cad_model, sample_polygon):
        """Test converting GEOS Polygon to CAD feature."""
        # When
        feature_id = cad_model.from_geos(sample_polygon)

        # Then
        assert feature_id is not None
        feature = cad_model.get_feature(feature_id)
        assert feature is not None
        assert hasattr(feature, "Shape")
        assert len(feature.Shape.Vertexes) == 4  # 4 points for a square (including closure)

    def test_to_geos_point(self, cad_model):
        """Test converting CAD feature to GEOS Point."""
        # Given
        params = {"Length": 10.0, "Width": 10.0, "Height": 10.0}
        feature_id = cad_model.create_feature("Box", params)

        # When
        geom = cad_model.to_geos(feature_id)

        # Then
        assert geom is not None
        assert isinstance(geom, Point)

    def test_invalid_feature_id(self, cad_model):
        """Test handling invalid feature ID in to_geos."""
        # When/Then
        with pytest.raises(ValidationError) as exc_info:
            cad_model.to_geos("invalid_id")
        assert "Invalid feature ID" in str(exc_info.value)

    def test_from_geos_invalid_geometry(self, cad_model):
        """Test handling invalid GEOS geometry."""
        # Given
        invalid_geom = None

        # When/Then
        with pytest.raises(ValidationError) as exc_info:
            cad_model.from_geos(invalid_geom)
        assert "Failed to convert GEOS geometry" in str(exc_info.value)

    def test_grid_alignment_after_conversion(self, cad_model, sample_point):
        """Test grid alignment is maintained after GEOS conversion."""
        # Given
        feature_id = cad_model.from_geos(sample_point)
        feature = cad_model.get_feature(feature_id)

        # Then
        assert hasattr(feature, "GridAligned")
        assert feature.GridAligned is True
        assert hasattr(feature, "GridDeviation")
        assert feature.GridDeviation < cad_model.grid_config.tolerance

    @pytest.mark.parametrize("coords", [
        (25.0, 25.0, 0.0),  # On grid
        (12.5, 12.5, 0.0),  # Half grid
        (33.3, 33.3, 0.0),  # Off grid
    ])
    def test_grid_snapping(self, cad_model, coords):
        """Test grid snapping behavior with various coordinates."""
        # Given
        point = Point(*coords)

        # When
        feature_id = cad_model.from_geos(point)
        feature = cad_model.get_feature(feature_id)

        # Then
        assert feature is not None
        if cad_model.grid_config.snap_enabled:
            deviation = feature.GridDeviation
            assert deviation <= cad_model.grid_config.tolerance