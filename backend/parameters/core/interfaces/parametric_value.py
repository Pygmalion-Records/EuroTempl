from dataclasses import dataclass
from typing import List, Dict, Any, Optional, Set
import concurrent.futures
from django.core.exceptions import ValidationError
from django.db import transaction
from core.models import Parameter, ParameterValue, Component, ComponentInstance
from ..cpp_extensions import ParameterGraphManager
from ...utils import UnitConverter
from geometry.cad_model import CADModel
from .parameter_constraint import ParameterConstraint


@dataclass
class ParametricValue:
    """
    Represents a parameter value with validation.

    Attributes:
        parameter_id (str): Unique identifier for the parameter.
        value (float): The numerical value of the parameter.
        unit (Optional[str]): Unit of measurement.
    """

    parameter_id: str
    value: float
    unit: Optional[str] = None

    def validate(self, constraint: ParameterConstraint) -> None:
        """Validate value against constraints."""
        if not isinstance(self.value, (int, float)):
            raise ValidationError("Invalid value type - must be numeric")
            
        # Convert units first if needed
        if constraint.unit and self.unit != constraint.unit:
            if UnitConverter.are_compatible(self.unit, constraint.unit):
                self.value = UnitConverter.convert(
                    self.value, self.unit, constraint.unit
                )
                self.unit = constraint.unit
            else:
                raise ValidationError(
                    f"Incompatible units: {self.unit} and {constraint.unit}"
                )
                
        # Then validate the converted value
        constraint.validate(self.value)
