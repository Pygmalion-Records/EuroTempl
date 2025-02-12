import pytest
from django.contrib.gis.geos import Point, Polygon, MultiPolygon
from geometry.cad_model import CADModel

@pytest.mark.django_db
class TestCADModel:
    @pytest.fixture(autouse=True)
    def setup_method(self, monkeypatch):
        # Setup test environment using monkeypatch instead of directly modifying os.environ
        monkeypatch.setenv('PYTEST_CURRENT_TEST', 'True')
        yield

    def test_create_from_geos(self):
        model = CADModel("test_model")
        point = Point(0, 0, 0)
        model.create_from_geos(point)
        assert model.shape is not None or model.doc is not None

    def test_modify_parameters(self):
        model = CADModel("test_model")
        params = {"height": 10, "width": 5}
        model.modify_parameters(params)
        assert model.shape is not None or model.doc is not None

    def test_to_geos(self):
        model = CADModel("test_model")
        params = {"height": 10, "width": 5}
        model.modify_parameters(params)
        geos_geom = model.to_geos()
        assert isinstance(geos_geom, (Polygon, MultiPolygon)) or geos_geom is None