from dataclasses import dataclass
from typing import List, Dict, Any, Optional, Set
import concurrent.futures
from django.core.exceptions import ValidationError
from django.db import transaction
from core.models import Parameter, ParameterValue, Component, ComponentInstance
from ..cpp_extensions import ParameterGraphManager
from ...utils import UnitConverter
from geometry.cad_model import CADModel


@dataclass
class ParameterConstraint:
    """
    Represents constraints for a parameter value.

    Attributes:
        min_value (Optional[float]): Minimum allowed value.
        max_value (Optional[float]): Maximum allowed value.
        step (Optional[float]): Step size for valid values.
        unit (Optional[str]): Unit of measurement.
    """

    min_value: Optional[float] = None
    max_value: Optional[float] = None
    step: Optional[float] = None
    unit: Optional[str] = None
    grid_aligned: bool = False

    def validate(self, value: float) -> None:
        """
        Validate a value against the constraints.

        Args:
            value (float): The value to validate.

        Raises:
            ValidationError: If the value violates any constraint.
        """
        if self.min_value is not None and value < self.min_value:
            raise ValidationError(f"Value {value} below minimum {self.min_value}")
        if self.max_value is not None and value > self.max_value:
            raise ValidationError(f"Value {value} above maximum {self.max_value}")
        if self.step is not None:
            if abs(value % self.step) > 1e-10:
                raise ValidationError(f"Value {value} must be a multiple of step {self.step}")

        if self.grid_aligned and abs(value % 25) > 1e-10:
                raise ValidationError("Value must align with 25mm grid")
