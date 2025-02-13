"""EuroTempl System
Copyright (c) 2024 Pygmalion Records"""

import os
import sys
import logging
from pathlib import Path
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)

class FreeCADGUIError(Exception):
    """Custom exception for FreeCAD GUI initialization errors."""
    pass

def get_qt_version() -> str:
    """Get the Qt version used by the system."""
    try:
        from PySide6.QtCore import __version__ as qt_version
        return qt_version
    except ImportError:
        return "Unknown"

def check_freecad_compatibility() -> Dict[str, Any]:
    """Check FreeCAD and Qt compatibility."""
    import FreeCAD
    
    info = {
        "freecad_version": FreeCAD.Version()[0],
        "qt_version": get_qt_version(),
        "python_version": sys.version.split()[0],
        "os_platform": sys.platform,
    }
    
    logger.info("FreeCAD Environment Info: %s", info)
    return info

def setup_gui_environment() -> None:
    """Setup environment variables for FreeCAD GUI."""
    conda_prefix = os.environ.get('CONDA_PREFIX')
    if not conda_prefix:
        raise FreeCADGUIError("CONDA_PREFIX not set. Are you in a conda environment?")

    # Essential paths
    paths = {
        'QT_PLUGIN_PATH': Path(conda_prefix) / 'lib' / 'qt' / 'plugins',
        'FREECAD_USER_HOME': Path.home() / '.FreeCAD',
        'FREECADPATH': Path(conda_prefix) / 'lib' / 'freecad',
        'PYTHONPATH': [
            Path(conda_prefix) / 'lib' / 'python3.10' / 'site-packages',
            Path(conda_prefix) / 'lib' / 'freecad',
            Path(conda_prefix) / 'Mod',
        ]
    }

    # Set environment variables
    for key, value in paths.items():
        if key == 'PYTHONPATH':
            for path in value:
                if path.exists() and str(path) not in sys.path:
                    sys.path.append(str(path))
        else:
            os.environ[key] = str(value)

def initialize_gui(headless: bool = True) -> Any:
    """Initialize FreeCAD GUI with robust error handling.
    
    Args:
        headless: If True, try to initialize in headless mode
    
    Returns:
        FreeCADGui module or None in headless mode
    
    Raises:
        FreeCADGUIError: If GUI initialization fails
    """
    try:
        # Setup environment
        setup_gui_environment()
        
        # Check compatibility
        compat_info = check_freecad_compatibility()
        logger.info("Initializing FreeCAD GUI with Qt %s", compat_info['qt_version'])
        
        if headless:
            os.environ['FREECAD_NOGUI'] = '1'
            return None
            
        # Import GUI
        import FreeCADGui
        
        # Verify GUI initialization
        if not FreeCADGui.getMainWindow():
            logger.warning("FreeCAD GUI initialized but main window not available")
            
        return FreeCADGui
        
    except ImportError as e:
        error_msg = f"Failed to import FreeCAD GUI: {e}"
        logger.error(error_msg)
        if "Symbol not found" in str(e):
            logger.error("Qt version mismatch detected. System Qt: %s", get_qt_version())
        raise FreeCADGUIError(error_msg) from e
        
    except Exception as e:
        error_msg = f"Unexpected error initializing FreeCAD GUI: {e}"
        logger.error(error_msg)
        raise FreeCADGUIError(error_msg) from e