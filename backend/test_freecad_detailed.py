import os
import sys

print("Environment variables:")
print(f"PYTHONPATH={os.environ.get('PYTHONPATH', 'Not set')}")
print(f"DYLD_FRAMEWORK_PATH={os.environ.get('DYLD_FRAMEWORK_PATH', 'Not set')}")
print(f"PATH_TO_FREECAD_LIBDIR={os.environ.get('PATH_TO_FREECAD_LIBDIR', 'Not set')}")

print("\nTrying to import pivy first...")
try:
    from pivy import coin
    print("Pivy imported successfully")
except ImportError as e:
    print(f"Pivy import error: {e}")

print("\nTrying to import FreeCAD modules...")
try:
    import freecad
    print("1. freecad imported")
    from freecad import Part
    print("2. Part imported")
    import FreeCAD
    print("3. FreeCAD imported")
except ImportError as e:
    print(f"Import error: {e}")
    print("\nDetailed sys.path:")
    for p in sys.path:
        print(f"  {p}")
        if os.path.exists(p):
            try:
                contents = os.listdir(p)
                print(f"    Contents: {contents[:5]}...")
            except Exception as e:
                print(f"    Error listing contents: {e}")
