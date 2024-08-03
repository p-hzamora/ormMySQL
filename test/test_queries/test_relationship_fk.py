import sys
from decouple import config
from pathlib import Path
import unittest

USERNAME = config("USERNAME")
PASSWORD = config("PASSWORD")

sys.path = [str(Path(__file__).parent.parent.parent), *sys.path]

from orm.utils import ForeignKey  # noqa: E402


class TestForeignKey(unittest.TestCase):
    def test_fk_with_staff_table_in_imports(self):
        self.assertDictEqual(ForeignKey.MAPPED, {})

        from test.models import Staff, Store, Address, City

        map = {
            City.__table_name__: ...,
            Address.__table_name__: ...,
            Store.__table_name__: ...,
            Staff.__table_name__: ...,
        }

        self.assertTupleEqual(tuple(ForeignKey.MAPPED), tuple(map))


if __name__ == "__main__":
    unittest.main()
