# TODOH: Studied how to set new tests for ForeignKey
import sys
from decouple import config
from pathlib import Path
import unittest
import importlib.util

USERNAME = config("USERNAME")
PASSWORD = config("PASSWORD")

sys.path.append([str(x) for x in Path(__file__).parents if x.name == "src"].pop())

from ormlambda.utils import ForeignKey  # noqa: E402



class TestForeignKey(unittest.TestCase): ...

if __name__ == "__main__":
    unittest.main()
