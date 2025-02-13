"""EuroTempl System
Copyright (c) 2024 Pygmalion Records"""

from dataclasses import dataclass

@dataclass
class GridConfig:
    """Configuration for grid system."""
    size: float = 25.0  # Grid size in mm
    snap_enabled: bool = True
    tolerance: float = 15.0  # Increased tolerance to handle half-grid points
    style: str = 'Lines'
    xy_only: bool = True  # Grid alignment only on X/Y axes
