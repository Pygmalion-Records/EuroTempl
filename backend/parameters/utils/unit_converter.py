
from dataclasses import dataclass

@dataclass
class UnitConverter:
    """Handles unit conversions and compatibility checks."""
    
    CONVERSION_FACTORS = {
        'length': {
            'mm': 1.0,
            'cm': 10.0,
            'm': 1000.0,
            'inch': 25.4
        },
        'area': {
            'mm2': 1.0,
            'cm2': 100.0,
            'm2': 1000000.0
        }
    }

    @classmethod
    def convert(cls, value: float, from_unit: str, to_unit: str) -> float:
        """Convert value between compatible units."""
        for unit_type, conversions in cls.CONVERSION_FACTORS.items():
            if from_unit in conversions and to_unit in conversions:
                return value * (conversions[from_unit] / conversions[to_unit])
        raise ValueError(f"Cannot convert between units {from_unit} and {to_unit}")

    @classmethod
    def are_compatible(cls, unit1: str, unit2: str) -> bool:
        """Check if units are compatible for conversion."""
        for conversions in cls.CONVERSION_FACTORS.values():
            if unit1 in conversions and unit2 in conversions:
                return True
        return False
