import sys
from pathlib import Path

sys.path = [str(Path(__file__).parent.parent.parent), *sys.path]

from src.test.models import Actor, Address, City, Country  # noqa: F401, E402
