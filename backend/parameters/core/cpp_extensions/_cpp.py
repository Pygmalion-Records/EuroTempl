"""EuroTempl System
Copyright (c) 2024 Pygmalion Records"""

class ParameterGraphManager:
    def __init__(self):
        self._parameters = {}

    def add_parameter(self, id: str, name: str, type: str, value: float) -> None:
        self._parameters[id] = {
            'name': name,
            'type': type,
            'value': value
        }