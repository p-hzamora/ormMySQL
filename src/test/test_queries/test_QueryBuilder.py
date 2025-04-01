import unittest
import sys
from pathlib import Path

sys.path.insert(0, [str(x.parent) for x in Path(__file__).parents if x.name == "test"].pop())


class TestQueryBuilder(unittest.TestCase): ...


if __name__ == "__main__":
    unittest.main()
