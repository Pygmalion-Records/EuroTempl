import sys
print("Python Path:")
for p in sys.path:
    print(f"  {p}")

print("\nTrying to import freecad...")
try:
    import freecad
    print(f"FreeCAD imported successfully from: {freecad.__file__}")
except ImportError as e:
    print(f"Import Error: {e}")

print("\nTrying to import Part...")
try:
    from freecad import Part
    print("Part module imported successfully")
except ImportError as e:
    print(f"Import Error: {e}")
