"""
EuroTempl System - Parametric Schema Implementation

This module implements the parametric schema for the EuroTempl system,
providing classes and functionality for managing parameter relationships,
constraints, and updates.

Copyright (c) 2024 Pygmalion Records
"""

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
from .parametric_value import ParametricValue

class ParameterManager:
    """
    Manages parametric relationships and updates.

    This class handles the creation, updating, and querying of parameters
    and their values, ensuring consistency and propagating changes through
    the parameter graph.
    """
    
    def __init__(self):
        """Initialize the ParameterManager."""
        self._graph = ParameterGraphManager()
        self._thread_pool = concurrent.futures.ThreadPoolExecutor(
            max_workers=4,
            thread_name_prefix="param_worker"
        )
        self._parameters: Dict[str, Parameter] = {}
        self._cad_models: Dict[str, CADModel] = {}
        self._load_parameters()

    def _load_parameters(self) -> None:
        """
        Load existing parameters from database.

        This method populates the internal parameter dictionary and graph
        with existing parameters from the database.
        """
        for param in Parameter.objects.all():
            self._parameters[str(param.id)] = param
            self._graph.add_parameter(
                str(param.id),
                param.name,
                param.data_type,
                self._get_current_value(param)
            )

    def _get_current_value(self, param: Parameter) -> float:
        """
        Get current value for a parameter.

        Args:
            param (Parameter): The parameter to get the value for.

        Returns:
            float: The current value of the parameter.
        """
        try:
            param_value = param.parametervalue_set.filter(
                validation_status='valid'
            ).latest('recorded_at')
            return param_value.value.get('value', 0.0)
        except ParameterValue.DoesNotExist:
            return 0.0

    @transaction.atomic
    def add_parameter(self, component: Component, name: str, 
                      data_type: str, constraints: ParameterConstraint) -> Parameter:
        """
        Add a new parameter to the system.

        Args:
            component (Component): The component the parameter belongs to.
            name (str): Name of the parameter.
            data_type (str): Data type of the parameter.
            constraints (ParameterConstraint): Constraints for the parameter.

        Returns:
            Parameter: The newly created parameter.
        """
        valid_ranges = {}
        if constraints.min_value is not None:
            valid_ranges['min'] = constraints.min_value
        if constraints.max_value is not None:
            valid_ranges['max'] = constraints.max_value
        if constraints.step is not None:
            valid_ranges['step'] = constraints.step
        if constraints.grid_aligned:
            valid_ranges['grid_aligned'] = constraints.grid_aligned

        param = Parameter.objects.create(
            component=component,
            name=name,
            data_type=data_type,
            units=constraints.unit,
            valid_ranges=valid_ranges,
            is_required=True
        )
        
        self._graph.add_parameter(
            str(param.id),
            name,
            data_type,
            0.0  # Default value
        )
        
        self._parameters[str(param.id)] = param
        return param

    def update_parameter(self, instance: ComponentInstance, 
                         param_id: str, new_value: ParametricValue, 
                         modified_by: str) -> List[str]:
        """
        Update parameter value and propagate changes.

        Args:
            instance (ComponentInstance): The instance being updated.
            param_id (str): ID of the parameter to update.
            new_value (ParametricValue): New value for the parameter.
            modified_by (str): Identifier of who modified the parameter.

        Returns:
            List[str]: List of affected parameter IDs.

        Raises:
            KeyError: If the parameter_id is not found.
        """
        if param_id not in self._parameters:
            raise KeyError(f"Parameter {param_id} not found")
    
        parameter = self._parameters[param_id]
        constraints = ParameterConstraint(
            min_value=parameter.valid_ranges.get('min'),
            max_value=parameter.valid_ranges.get('max'),
            step=parameter.valid_ranges.get('step'),
            unit=parameter.units,
            grid_aligned=parameter.valid_ranges.get('grid_aligned', False)
        )
        
        new_value.validate(constraints)
        
        with transaction.atomic():
            ParameterValue.objects.create(
                instance=instance,
                parameter=parameter,
                value={
                    'value': new_value.value,
                    'unit': new_value.unit
                },
                validation_status='valid',
                modified_by=modified_by
            )
            
            self._graph.update_value(param_id, new_value.value)
            affected = self._graph.get_affected_parameters(param_id)
            
            futures = []
            for affected_id in affected:
                futures.append(
                    self._thread_pool.submit(
                        self._update_dependent, 
                        instance, 
                        affected_id,
                        modified_by
                    )
                )
            concurrent.futures.wait(futures)
            
            return affected
    
    def _update_dependent(self, instance: ComponentInstance, param_id: str, 
                          modified_by: str) -> None:
        """
        Update a dependent parameter based on relationship rules.

        Args:
            instance (ComponentInstance): The instance being updated.
            param_id (str): ID of the parameter to update.
            modified_by (str): Identifier of who modified the parameter.
        """
        parameter = self._parameters[param_id]
        new_value = self._graph.get_parameter_value(param_id)
        
        ParameterValue.objects.create(
            instance=instance,
            parameter=parameter,
            value={
                'value': new_value,
                'unit': parameter.units
            },
            validation_status='valid',
            modified_by=modified_by
        )
        
    def get_parameter_values(self, instance: ComponentInstance) -> Dict[str, float]:
        """
        Get current values for all parameters of an instance.

        Args:
            instance (ComponentInstance): The instance to get values for.

        Returns:
            Dict[str, float]: Dictionary of parameter IDs to their current values.
        """
        values = {}
        for param_id, param in self._parameters.items():
            try:
                value = ParameterValue.objects.filter(
                    instance=instance,
                    parameter=param,
                    validation_status='valid'
                ).latest('recorded_at')
                values[param_id] = value.value.get('value')
            except ParameterValue.DoesNotExist:
                values[param_id] = 0.0
        return values

    def validate_grid_alignment(self, value: float) -> bool:
        """
        Validate alignment with 25mm grid.

        Args:
            value (float): The value to validate.

        Returns:
            bool: True if the value is aligned with the 25mm grid, False otherwise.
        """
        return abs(value % 25) < 1e-10

    def get_dependent_parameters(self, param_id: str) -> Set[str]:
        """
        Get parameters that depend on the given parameter.

        Args:
            param_id (str): ID of the parameter to check dependencies for.

        Returns:
            Set[str]: Set of dependent parameter IDs.
        """
        return set(self._graph.get_affected_parameters(param_id))