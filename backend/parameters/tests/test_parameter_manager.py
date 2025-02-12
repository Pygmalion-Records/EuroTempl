"""EuroTempl System
Copyright (c) 2024 Pygmalion Records"""

import pytest
from unittest.mock import Mock
from django.core.exceptions import ValidationError
from ..core.interfaces.parameter_manager import ParameterManager, ParametricValue, ParameterConstraint
from core.models import Component, ComponentInstance, ComponentStatus
from core.tests import valid_component_data
from geometry.cad_model import CADModel

@pytest.fixture
def mock_cad_model():
    """Fixture providing a mock CAD model."""
    mock = Mock(spec=CADModel)
    mock.id = "test_model_id"
    return mock

@pytest.fixture
def test_user():
    """Fixture providing a test user."""
    from django.contrib.auth import get_user_model
    User = get_user_model()
    
    # Try to get existing user first
    try:
        user = User.objects.get(username='testuser')
    except User.DoesNotExist:
        # Create new user if doesn't exist
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
    return user

@pytest.fixture(autouse=True)
def cleanup_db():
    """Clean up the database before and after each test."""
    ComponentInstance.objects.all().delete()  # Delete instances first
    Component.objects.all().delete()         # Then delete components
    yield
    ComponentInstance.objects.all().delete()  # Clean up in reverse order
    Component.objects.all().delete()

@pytest.fixture
def component(valid_component_data):
    """Fixture providing a valid component for parameter testing."""
    return Component.objects.create(**valid_component_data)

@pytest.fixture
def valid_instance_data(valid_component_data):
    """Fixture providing valid component instance data."""
    from django.contrib.gis.geos import GEOSGeometry
    
    wkt = 'POLYGON Z ((0 0 0, 0 25 0, 25 25 0, 25 0 0, 0 0 0))'
    geometry = GEOSGeometry(wkt, srid=4326)
    bbox = geometry.envelope
    
    return {
        'component': valid_component_data,
        'spatial_data': geometry,
        'spatial_bbox': bbox,
        'internal_id': 1,
        'instance_properties': {
            'material': 'steel',
            'finish': 'matte'
        },
        'status': ComponentStatus.PLANNED.value,
        'version': 1
    }
    

@pytest.fixture
def instance(component, valid_instance_data):
    """Fixture providing a valid component instance for parameter testing."""
    instance_data = valid_instance_data.copy()  # Create a copy of the data
    instance_data['component'] = component  # Override the component reference
    return ComponentInstance.objects.create(**instance_data)


@pytest.fixture
def manager():
    return ParameterManager()

class TestParameterManager:
    def test_add_parameter(self, manager, component):
        constraints = ParameterConstraint(
            min_value=0.0,
            max_value=200.0,
            step=1.0,
            unit="mm"
        )
        param = manager.add_parameter(
            component=component,
            name="Test Parameter",
            data_type="float",
            constraints=constraints
        )
        assert str(param.id) in manager._parameters

    def test_update_parameter(self, manager, component, instance, test_user):
        constraints = ParameterConstraint(
            min_value=0.0,
            max_value=200.0,
            step=1.0,
            unit="mm"
        )
        param = manager.add_parameter(
            component=component,
            name="Test Parameter",
            data_type="float",
            constraints=constraints
        )
    
        new_value = ParametricValue(
            parameter_id=str(param.id),
            value=150.0,
            unit="mm"
        )
        # Add modified_by as it's required by the model
        affected = manager.update_parameter(instance, str(param.id), new_value, modified_by=test_user)
        
        # Verify the update
        values = manager.get_parameter_values(instance)
        assert values[str(param.id)] == 150.0
    
    def test_parameter_dependencies(self, manager, component, instance, test_user):
        """Test parameter dependency management and calculations."""
        width_constraints = ParameterConstraint(
            min_value=0.0,
            max_value=1000.0,
            step=1.0,
            unit="mm"
        )
        area_constraints = ParameterConstraint(
            min_value=0.0,
            max_value=1000000.0,
            step=1.0,
            unit="mm²"
        )
    
        # Create parameters
        width_param = manager.add_parameter(
            component=component,
            name="Width",
            data_type="float",
            constraints=width_constraints
        )
    
        height_param = manager.add_parameter(
            component=component,
            name="Height",
            data_type="float",
            constraints=width_constraints
        )
    
        area_param = manager.add_parameter(
            component=component,
            name="Area",
            data_type="float",
            constraints=area_constraints
        )
    
        # Set initial values first
        width_value = ParametricValue(
            parameter_id=str(width_param.id),
            value=100.0,
            unit="mm"
        )
        height_value = ParametricValue(
            parameter_id=str(height_param.id),
            value=50.0,
            unit="mm"
        )
    
        # Update initial values
        manager.update_parameter(instance, str(width_param.id), width_value, modified_by=test_user)
        manager.update_parameter(instance, str(height_param.id), height_value, modified_by=test_user)
    
        # Now add dependencies
        manager._graph.add_dependency(
            str(area_param.id),
            str(width_param.id),
            "width * height"
        )
        manager._graph.add_dependency(
            str(area_param.id),
            str(height_param.id),
            "width * height"
        )
    
        # Force recalculation
        manager._graph._recalculate_dependencies()
        manager._update_dependent(
            instance=instance,
            param_id=str(area_param.id),
            modified_by=test_user
        )
    
        values = manager.get_parameter_values(instance)
        assert values[str(area_param.id)] == 5000.0  # 100mm * 50mm = 5000mm²
    def test_grid_aligned_parameter(self, manager, component, instance, test_user):
        """Test parameter with grid alignment constraint."""
        constraints = ParameterConstraint(
            min_value=0.0,
            max_value=1000.0,
            step=1.0,
            unit="mm",
            grid_aligned=True
        )
        
        param = manager.add_parameter(
            component=component,
            name="Grid Aligned Parameter",
            data_type="float",
            constraints=constraints
        )
        
        # Test valid grid-aligned value (multiple of 25mm)
        valid_value = ParametricValue(
            parameter_id=str(param.id),
            value=75.0,  # 3 * 25mm
            unit="mm"
        )
        manager.update_parameter(instance, str(param.id), valid_value, modified_by=test_user)
        values = manager.get_parameter_values(instance)
        assert values[str(param.id)] == 75.0
    
    def test_grid_aligned_parameter_invalid(self, manager, component, instance, test_user):
        """Test parameter with grid alignment constraint fails for non-aligned values."""
        constraints = ParameterConstraint(
            min_value=0.0,
            max_value=1000.0,
            step=1.0,
            unit="mm",
            grid_aligned=True
        )
        
        param = manager.add_parameter(
            component=component,
            name="Grid Aligned Parameter",
            data_type="float",
            constraints=constraints
        )
        
        # Test invalid non-grid-aligned value
        invalid_value = ParametricValue(
            parameter_id=str(param.id),
            value=77.0,  # Not a multiple of 25mm
            unit="mm"
        )
        
        with pytest.raises(ValidationError) as exc_info:
            manager.update_parameter(instance, str(param.id), invalid_value, modified_by=test_user)
        assert "Value must align with 25mm grid" in str(exc_info.value)
    
    def test_grid_alignment_with_other_constraints(self, manager, component, instance, test_user):
        """Test grid alignment works together with other constraints."""
        constraints = ParameterConstraint(
            min_value=50.0,
            max_value=100.0,
            step=25.0,  # Step size matches grid
            unit="mm",
            grid_aligned=True
        )
        
        param = manager.add_parameter(
            component=component,
            name="Grid Aligned Parameter",
            data_type="float",
            constraints=constraints
        )
        
        # Test valid value that satisfies both grid and step constraints
        valid_value = ParametricValue(
            parameter_id=str(param.id),
            value=75.0,  # Multiple of both 25mm grid and step size
            unit="mm"
        )
        manager.update_parameter(instance, str(param.id), valid_value, modified_by=test_user)
        values = manager.get_parameter_values(instance)
        assert values[str(param.id)] == 75.0
        
        # Test value that satisfies grid but violates min constraint
        invalid_value = ParametricValue(
            parameter_id=str(param.id),
            value=25.0,  # Grid aligned but below min_value
            unit="mm"
        )
        
        with pytest.raises(ValidationError) as exc_info:
            manager.update_parameter(instance, str(param.id), invalid_value, modified_by=test_user)
        assert "below minimum" in str(exc_info.value)
    
    def test_unit_conversion(self, manager, component, instance, test_user):
        """Test automatic unit conversion during parameter validation."""
        constraints = ParameterConstraint(
            min_value=0.0,
            max_value=2000.0,
            step=1.0,
            unit="mm"
        )
        
        param = manager.add_parameter(
            component=component,
            name="Length Parameter",
            data_type="float",
            constraints=constraints
        )
        
        # Test value in meters gets converted to millimeters
        value_in_meters = ParametricValue(
            parameter_id=str(param.id),
            value=1.5,  # 1.5m = 1500mm
            unit="m"
        )
        
        manager.update_parameter(instance, str(param.id), value_in_meters, modified_by=test_user)
        values = manager.get_parameter_values(instance)
        assert values[str(param.id)] == 1500.0  # Verify conversion to mm
    
    def test_incompatible_unit_conversion(self, manager, component, instance, test_user):
        """Test validation fails for incompatible units."""
        constraints = ParameterConstraint(
            min_value=0.0,
            max_value=1000.0,
            step=1.0,
            unit="mm"
        )
        
        param = manager.add_parameter(
            component=component,
            name="Length Parameter",
            data_type="float",
            constraints=constraints
        )
        
        # Test value with incompatible unit (degrees)
        invalid_value = ParametricValue(
            parameter_id=str(param.id),
            value=45.0,
            unit="deg"
        )
        
        with pytest.raises(ValidationError) as exc_info:
            manager.update_parameter(instance, str(param.id), invalid_value, modified_by=test_user)
        assert "Incompatible units" in str(exc_info.value)
    
    def test_non_numeric_value_validation(self, manager, component, instance, test_user):
        """Test validation handles non-numeric values appropriately."""
        constraints = ParameterConstraint(
            min_value=0.0,
            max_value=1000.0,
            unit="mm",
            step=None  # Remove step constraint
        )
        
        param = manager.add_parameter(
            component=component,
            name="Length Parameter",
            data_type="float",
            constraints=constraints
        )
        
        # Test with non-numeric value
        invalid_value = ParametricValue(
            parameter_id=str(param.id),
            value="not a number",
            unit="mm"
        )
        
        with pytest.raises(ValidationError) as exc_info:
            manager.update_parameter(instance, str(param.id), invalid_value, modified_by=test_user)
        assert "Invalid value type" in str(exc_info.value)
    
    def test_cad_models_initialization(self, manager):
        """Test that CAD models dictionary is properly initialized."""
        assert isinstance(manager._cad_models, dict)
        assert len(manager._cad_models) == 0
    
    def test_cad_models_operations(self, manager, mock_cad_model):
        """Test adding and retrieving CAD models."""
        # Add CAD model
        manager._cad_models[mock_cad_model.id] = mock_cad_model
        
        # Verify retrieval
        assert manager._cad_models[mock_cad_model.id] == mock_cad_model
        assert len(manager._cad_models) == 1
    
    def test_cad_models_cleanup(self, manager, mock_cad_model):
        """Test proper cleanup of CAD models."""
        # Add CAD model
        manager._cad_models[mock_cad_model.id] = mock_cad_model
        
        # Clear dictionary
        manager._cad_models.clear()
        
        # Verify cleanup
        assert len(manager._cad_models) == 0
        assert mock_cad_model.id not in manager._cad_models