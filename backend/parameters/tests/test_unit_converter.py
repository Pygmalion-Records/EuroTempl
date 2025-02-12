"""
EuroTempl System - Unit Converter Tests

This module contains tests for the unit conversion functionality.

Copyright (c) 2024 Pygmalion Records
"""

import pytest
from ..utils.unit_converter import UnitConverter

def test_length_conversions():
    """Test basic length unit conversions."""
    # mm to cm
    assert UnitConverter.convert(100.0, "mm", "cm") == pytest.approx(10.0)
    # cm to m
    assert UnitConverter.convert(100.0, "cm", "m") == pytest.approx(1.0)
    # mm to m
    assert UnitConverter.convert(1000.0, "mm", "m") == pytest.approx(1.0)
    # inch to mm
    assert UnitConverter.convert(1.0, "inch", "mm") == pytest.approx(25.4)

def test_area_conversions():
    """Test area unit conversions."""
    # mm2 to cm2
    assert UnitConverter.convert(100.0, "mm2", "cm2") == pytest.approx(1.0)
    # cm2 to m2
    assert UnitConverter.convert(10000.0, "cm2", "m2") == pytest.approx(1.0)
    # mm2 to m2
    assert UnitConverter.convert(1000000.0, "mm2", "m2") == pytest.approx(1.0)

def test_invalid_conversions():
    """Test error handling for invalid unit conversions."""
    with pytest.raises(ValueError) as exc_info:
        UnitConverter.convert(100.0, "mm", "kg")
    assert "Cannot convert between units" in str(exc_info.value)

    with pytest.raises(ValueError) as exc_info:
        UnitConverter.convert(100.0, "mm2", "mm")
    assert "Cannot convert between units" in str(exc_info.value)

def test_unit_compatibility():
    """Test unit compatibility checks."""
    # Length units
    assert UnitConverter.are_compatible("mm", "cm") is True
    assert UnitConverter.are_compatible("mm", "m") is True
    assert UnitConverter.are_compatible("inch", "mm") is True
    
    # Area units
    assert UnitConverter.are_compatible("mm2", "cm2") is True
    assert UnitConverter.are_compatible("mm2", "m2") is True
    
    # Incompatible units
    assert UnitConverter.are_compatible("mm", "mm2") is False
    assert UnitConverter.are_compatible("mm", "invalid") is False
    assert UnitConverter.are_compatible("invalid1", "invalid2") is False

def test_roundtrip_conversions():
    """Test roundtrip conversions return to original value."""
    original_value = 100.0
    
    # mm -> cm -> mm
    intermediate = UnitConverter.convert(original_value, "mm", "cm")
    result = UnitConverter.convert(intermediate, "cm", "mm")
    assert result == pytest.approx(original_value)
    
    # mm -> m -> mm
    intermediate = UnitConverter.convert(original_value, "mm", "m")
    result = UnitConverter.convert(intermediate, "m", "mm")
    assert result == pytest.approx(original_value)

def test_precision():
    """Test conversion precision for small values."""
    # Test small measurements (0.1mm)
    small_value = 0.1
    converted = UnitConverter.convert(small_value, "mm", "m")
    assert converted == pytest.approx(0.0001)
    
    # Test very small measurements (0.001mm)
    very_small = 0.001
    converted = UnitConverter.convert(very_small, "mm", "m")
    assert converted == pytest.approx(0.000001)

@pytest.mark.parametrize("value,from_unit,to_unit,expected", [
    (1000.0, "mm", "m", 1.0),
    (1.0, "m", "mm", 1000.0),
    (100.0, "cm2", "m2", 0.01),
    (1.0, "inch", "mm", 25.4),
])
def test_parametrized_conversions(value, from_unit, to_unit, expected):
    """Test various conversion combinations."""
    result = UnitConverter.convert(value, from_unit, to_unit)
    assert result == pytest.approx(expected)