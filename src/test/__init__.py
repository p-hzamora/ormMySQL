import sys
from pathlib import Path

inserted_file = str(Path(__file__).parent.parent)
if inserted_file != sys.path[0]:
    sys.path.insert(0, inserted_file)
