"""
Manages the parameter dependency graph for the EuroTempl system.

This module provides a ParameterGraphManager class that handles parameter
relationships, dependencies, and value calculations.

Copyright (c) 2024 Pygmalion Records
"""

class ParameterGraphManager:
    """
    Manages the parameter dependency graph.

    This class handles the storage, updating, and calculation of
    interdependent parameters within the system.

    Attributes:
        _parameters (dict): Stores parameter metadata.
        _values (dict): Stores current parameter values.
        _dependencies (dict): Stores dependency relationships between parameters.
        _formulas (dict): Stores calculation formulas for dependent parameters.
    """

    def __init__(self):
        """
        Initialize a new ParameterGraphManager instance.
        """
        self._parameters = {}
        self._values = {}
        self._dependencies = {}
        self._formulas = {}

    def add_parameter(self, param_id: str, name: str, data_type: str, initial_value: float) -> None:
        """
        Add a new parameter to the graph.

        Args:
            param_id (str): Unique identifier for the parameter.
            name (str): Human-readable name of the parameter.
            data_type (str): Data type of the parameter.
            initial_value (float): Initial value of the parameter.
        """
        self._parameters[param_id] = {
            'name': name,
            'type': data_type
        }
        self._values[param_id] = initial_value

    def update_value(self, param_id: str, value: float) -> None:
        """
        Update a parameter's value and recalculate dependencies.

        Args:
            param_id (str): Identifier of the parameter to update.
            value (float): New value for the parameter.

        Raises:
            KeyError: If the parameter_id is not found in the graph.
        """
        if param_id not in self._values:
            raise KeyError(f"Parameter {param_id} not found")
        self._values[param_id] = value
        self._recalculate_dependencies()

    def get_parameter_value(self, param_id: str) -> float:
        """
        Get the current value of a parameter.

        Args:
            param_id (str): Identifier of the parameter.

        Returns:
            float: Current value of the parameter.

        Raises:
            KeyError: If the parameter_id is not found in the graph.
        """
        if param_id not in self._values:
            raise KeyError(f"Parameter {param_id} not found")
        return self._values[param_id]

    def add_dependency(self, source: str, target: str, formula: str) -> None:
        """
        Add a dependency between parameters.

        Args:
            source (str): Identifier of the source (dependent) parameter.
            target (str): Identifier of the target parameter.
            formula (str): Formula to calculate the source parameter's value.
        """
        if source not in self._dependencies:
            self._dependencies[source] = set()
        self._dependencies[source].add(target)
        self._formulas[source] = formula

    def get_affected_parameters(self, param_id: str) -> list[str]:
        """
        Get list of parameters affected by changes to a specific parameter.

        Args:
            param_id (str): Identifier of the parameter to check.

        Returns:
            list[str]: List of parameter identifiers affected by param_id.
        """
        affected = []
        for source, deps in self._dependencies.items():
            if param_id in deps:
                affected.append(source)
        return affected

    def _recalculate_dependencies(self) -> None:
        """
        Recalculate all dependent parameters.

        This method updates the values of all dependent parameters
        based on their formulas and the current values of their
        dependencies.
        """
        for source, deps in self._dependencies.items():
            if source in self._formulas:
                formula = self._formulas[source]
                # For this simple example, we just multiply the values
                # In a real implementation, you'd want to parse and evaluate the formula
                result = 1.0
                for dep in deps:
                    result *= self._values.get(dep, 0.0)
                self._values[source] = result