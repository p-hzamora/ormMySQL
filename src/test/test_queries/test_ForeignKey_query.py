# TODOH: Studied how to set new tests for ForeignKey
import sys
from decouple import config
from pathlib import Path
import unittest

USERNAME = config("USERNAME")
PASSWORD = config("PASSWORD")

sys.path.append([str(x) for x in Path(__file__).parents if x.name == "src"].pop())
sys.path.append([str(x) for x in Path(__file__).parents if x.name == "test"].pop())


from ormlambda.utils import ForeignKey  # noqa: E402
from models import Address, City  # noqa: E402


class TestForeignKey(unittest.TestCase):
    def test_init_with_comparer(self):
        comparer = Address.city_id == City.city_id
        fk = ForeignKey(comparer=comparer, clause_name="FK between A~C")

        self.assertIsInstance(fk, ForeignKey)

        self.assertEqual(fk._relationship, None)
        self.assertEqual(fk.tleft, Address)
        self.assertEqual(fk.tright, City)
        self.assertEqual(fk.clause_name, "FK between A~C")
        self.assertEqual(fk._comparer, comparer)

    def test_init_with_callable(self):
        def fn(a: Address, c: City):
            return a.city_id == c.city_id

        fk: ForeignKey = ForeignKey[Address, City](City, fn)

        self.assertIsInstance(fk, ForeignKey)

        self.assertEqual(fk._relationship, fn)
        self.assertEqual(fk.tleft, None)
        self.assertEqual(fk.tright, City)
        self.assertEqual(fk.clause_name, None)
        self.assertEqual(fk._comparer, None)


if __name__ == "__main__":
    unittest.main()
