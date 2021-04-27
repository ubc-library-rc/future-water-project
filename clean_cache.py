import sys
from pathlib import Path

if len(sys.argv) != 2:
    raise Exception(
        "Expected a single argument, e.g.:\n\tpython clean_cache.py alice")

for p in Path("./resources").rglob(f"*{sys.argv[1].lower()}*.json"):
    print(f"Deleting {str(p)}")
    p.unlink()

for p in Path("./resources").rglob(f"*{sys.argv[1].lower()}*.csv"):
    print(f"Deleting {str(p)}")
    p.unlink()
