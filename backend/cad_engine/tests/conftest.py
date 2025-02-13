"""EuroTempl System
Copyright (c) 2024 Pygmalion Records"""

import os
import sys
import pytest
from pathlib import Path
from ..utils.gui_helper import initialize_gui

def pytest_configure():
    """Configure test environment."""
    conda_prefix = os.environ.get('CONDA_PREFIX')
    if not conda_prefix:
        pytest.skip("CONDA_PREFIX not set")
        
    # Add FreeCAD paths
    freecad_paths = [
        Path(conda_prefix) / 'lib',
        Path(conda_prefix) / 'lib' / 'freecad',
        Path(conda_prefix) / 'Mod',
        Path(conda_prefix) / 'bin'
    ]
    
    for path in freecad_paths:
        if path.exists() and str(path) not in sys.path:
            sys.path.append(str(path))

@pytest.fixture(scope='session')
def freecad_env():
    """Initialize FreeCAD environment."""
    try:
        import FreeCAD
        Gui = initialize_gui()
        return {'App': FreeCAD, 'Gui': Gui}
    except ImportError as e:
        pytest.skip(f"FreeCAD import failed: {e}")