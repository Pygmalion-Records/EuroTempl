"""EuroTempl System
Copyright (c) 2024 Pygmalion Records

Parameter model implementation for the EuroTempl system.
This model defines parametric attributes that can be assigned to components,
serving as a crucial element in implementing parametric design principles.
"""

from django.db import models
from django.db.models import JSONField
from django.core.exceptions import ValidationError
from django.core.validators import MinLengthValidator
import uuid
from typing import Dict, Any

class Parameter(models.Model):
    """
    The Parameter model defines and manages the parametric attributes that can be
    assigned to components in the EuroTempl system. It serves as a bridge between
    abstract component definitions and their concrete implementations.
    """

    # Core fields
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        help_text="Unique identifier for the parameter"
    )

    component = models.ForeignKey(
        'Component',
        on_delete=models.CASCADE,
        help_text="Reference to parent component"
    )

    name = models.CharField(
        max_length=100,
        validators=[MinLengthValidator(2)],
        help_text="Name of the parameter"
    )

    data_type = models.CharField(
        max_length=50,
        choices=[
            ('float', 'Float'),
            ('integer', 'Integer'),
            ('text', 'Text'),
            ('boolean', 'Boolean'),
            ('json', 'JSON'),
            ('geometry', 'Geometry')
        ],
        help_text="Specifies the parameter's data type"
    )

    units = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        help_text="Units of measurement for the parameter"
    )

    valid_ranges = JSONField(
        default=dict,
        blank=True, 

        help_text="Defines acceptable value ranges and constraints"
    )

    is_required = models.BooleanField(
        default=False,
        help_text="Indicates if parameter is mandatory"
    )

    description = models.TextField(
        blank=True,
        help_text="Detailed parameter description"
    )

    # Timestamps for tracking
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'et_parameter'
        indexes = [
            models.Index(fields=['component']),
            models.Index(fields=['name']),
            models.Index(fields=['data_type']),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=['component', 'name'],
                name='unique_parameter_name_per_component'
            )
        ]

    def clean(self) -> None:
        """
        Validate the parameter according to EuroTempl business rules.
        """
        self._validate_units()
        self._validate_valid_ranges()
        super().clean()

    def _validate_units(self) -> None:
        """
        Validate that units are provided when required and follow standard formats.
        """
        numeric_types = {'float', 'integer'}
        if self.data_type in numeric_types and not self.units:
            raise ValidationError({
                'units': 'Units must be specified for numeric parameters'
            })

    def _validate_valid_ranges(self) -> None:
        """
        Validate that valid_ranges field contains appropriate constraints for the data type.
        """
        if not isinstance(self.valid_ranges, dict):
            raise ValidationError({
                'valid_ranges': 'Valid ranges must be a dictionary'
            })

        if self.data_type in {'float', 'integer'}:
            required_keys = {'min', 'max'}
            if not all(key in self.valid_ranges for key in required_keys):
                raise ValidationError({
                    'valid_ranges': 'Numeric parameters must specify min and max values'
                })

            if ('step' in self.valid_ranges and 
                not isinstance(self.valid_ranges['step'], (int, float))):
                raise ValidationError({
                    'valid_ranges': 'Step value must be numeric'
                })

    def validate_value(self, value: Any) -> bool:
        """
        Validate a given value against this parameter's constraints.

        Args:
            value: The value to validate

        Returns:
            bool: True if the value is valid, False otherwise

        Raises:
            ValidationError: If the value violates any constraints
        """
        if value is None:
            if self.is_required:
                raise ValidationError(f"Parameter {self.name} is required")
            return True

        # Type validation
        if self.data_type == 'float':
            if not isinstance(value, (int, float)):
                raise ValidationError(f"Value must be numeric for parameter {self.name}")
        elif self.data_type == 'integer':
            if not isinstance(value, int):
                raise ValidationError(f"Value must be an integer for parameter {self.name}")
        elif self.data_type == 'boolean':
            if not isinstance(value, bool):
                raise ValidationError(f"Value must be boolean for parameter {self.name}")
        elif self.data_type == 'json':
            if not isinstance(value, dict):
                raise ValidationError(f"Value must be a dictionary for parameter {self.name}")

        # Range validation for numeric types
        if self.data_type in {'float', 'integer'} and self.valid_ranges:
            min_val = self.valid_ranges.get('min')
            max_val = self.valid_ranges.get('max')
            step = self.valid_ranges.get('step')

            if min_val is not None and value < min_val:
                raise ValidationError(f"Value must be >= {min_val} for parameter {self.name}")
            if max_val is not None and value > max_val:
                raise ValidationError(f"Value must be <= {max_val} for parameter {self.name}")
            if step is not None:
                if not self._is_valid_step(value, step, min_val):
                    raise ValidationError(
                        f"Value must be in steps of {step} from {min_val} for parameter {self.name}"
                    )

        return True

    def _is_valid_step(self, value: float, step: float, min_val: float) -> bool:
        """
        Check if a value follows the step constraint from the minimum value.

        Args:
            value (float): The value to check
            
            step (float): The step size
            min_val (float): The minimum value

        Returns:
            bool: True if the value follows the step constraint
        """
        if min_val is None:
            min_val = 0
        # Account for floating point precision issues
        tolerance = 1e-10
        steps_from_min = (value - min_val) / step
        return abs(round(steps_from_min) - steps_from_min) < tolerance

    def get_values(self):
        """
        Retrieve all ParameterValue instances associated with this parameter.

        Returns:
            QuerySet: All ParameterValue instances for this parameter
        """
        return self.parametervalue_set.all()

    def save(self, *args, **kwargs):
        """
        Override save to ensure validation is always performed.
        """
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        """
        String representation of the parameter.

        Returns:
            str: A string describing the parameter
        """
        return f"{self.component.name} - {self.name} ({self.data_type})"